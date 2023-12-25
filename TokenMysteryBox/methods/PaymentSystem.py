# Imports
from solana.publickey import PublicKey
from CoreMysteryBox import settings
from CoreMysteryBox.general_methods import FindTxSignatures, SolanaTransfer
from solana.rpc.commitment import Commitment
from TokenMysteryBox.models import tokenmysterybox
from solana.rpc.api import Client
from . import TokenMethods
import time, threading

# Variables for temporary data storage (Faster then database calls)
SIGNING_PUBKEY = 0
SIGNATURE = 0
TRANSACTION_AMOUNT = 0
TOKEN_ACCOUNT = 0
TACSIGNATURE = 0
TOKENMINTERSIGNATURE = 0
TOKENREWARDAMOUNT = 0

# First part of the token mystery box payment system.
def TokenMB_PaymentSystem1(my_address, price1):
    global SIGNING_PUBKEY, SIGNATURE, TRANSACTION_AMOUNT, TOKEN_ACCOUNT
    # Variable for the "Checking_for_new_transaction" method
    signature = "Placeholder"
    # Function to execute in a separate thread
    def Checking_for_new_transaction():
        nonlocal signature
        # Checking for new transaction.
        try:
            signature = FindTxSignatures.find_transaction(tokenmysterybox, my_address)
        except Exception as e:
            if isinstance(e, AttributeError):
                # While executing this section of the payment system within the tests, an anticipated 
                # error arises. However, I face difficulty in explicitly raising it here. 
                # So, I manage the error further along in the primary segment of the view.
                return "expected_test_error"
            else: 
                raise e
    # Create a new thread and start it
    thread = threading.Thread(target=Checking_for_new_transaction)
    thread.start()
    # Wait for the thread to complete or timeout after 6 seconds
    thread.join(timeout=6)
    # If the thread is still running after 6 seconds (timeout), terminate the thread
    if thread.is_alive():
        return "timeout"  # Return "timeout" indicating timeout
    # If the signature received from find_transaction is "NoNewTransaction", return it
    if signature == "NoNewTransaction":
        return signature
    # Variable for the "Get_Transaction" method
    transaction_info = "Placeholder"
    # Function to execute in a separate thread
    def Get_Transaction():
        nonlocal transaction_info
        # Client for the blockchain.
        solana_client = Client(settings.SOLANA_API_URL)
        # Get more transaction info
        transaction_info = solana_client.get_transaction(tx_sig = signature, commitment=Commitment("confirmed"))
    # Create a new thread and start it
    thread = threading.Thread(target=Get_Transaction)
    thread.start()
    # Wait for the thread to complete or timeout after 4.5 seconds
    thread.join(timeout=4.5)
    # If the thread is still running after 4.5 seconds (timeout), terminate the thread
    if thread.is_alive():
        return "timeout" # Return "timeout" indicating timeout
    # Extracting the transaction amount in Solana
    postbalance = transaction_info["result"]["meta"]["postBalances"][1]
    prebalance = transaction_info["result"]["meta"]["preBalances"][1]
    transaction_amount = (postbalance - prebalance) / 1e9 # Number of lamports (1 Billion)
    # Extracting the public key of the recipent
    recipent_pubkey = transaction_info["result"]["transaction"]["message"]["accountKeys"][1]
    # Extracting the public key of the sender (buyer)
    signing_pubkey = transaction_info["result"]["transaction"]["message"]["accountKeys"][0]
    # Check for already created token account for this payment
    # This means that I created a token account for this payment, but don't mint the tokens to it
    if TOKEN_ACCOUNT != 0:
        SIGNATURE = signature
        TRANSACTION_AMOUNT = transaction_amount
        return "Already created token account"
    # Verifying the correctness of the transaction
    if transaction_amount <= 0 or recipent_pubkey != my_address:
        # Retrieve the first row from the database
        first_record = tokenmysterybox.objects.first()
        first_record.transactions = signature
        first_record.save()
        return "NoValidTransaction"
    # If the amount is insufficient, I transfer back the 
    # amount - expected fee to the buyer if positive
    if transaction_amount < price1:
        # Extract the fee.
        fee = transaction_info["result"]["meta"]["fee"]
        # Extract the transaction amount - fee (In lamports)
        txAmount = (postbalance - prebalance)-fee
        if txAmount <= 0:
            # Retrieve the first row from the database
            first_record = tokenmysterybox.objects.first()
            first_record.transactions = signature
            first_record.save()
            return "NoValidTransaction"
        # Send back the transaction amount.
        RPCResponse = SolanaTransfer.Solana_transfer(
            sender_privatekey=settings.TokenMB_Privatekey,
            recipient_pubkey=PublicKey(signing_pubkey), 
            amount=txAmount)
        # Retrieve the first row from the database
        first_record = tokenmysterybox.objects.first()
        first_record.transactions = signature
        first_record.save()
        time.sleep(2) # Wait for the solana transfer transaction to get at least "confirmed" status
        # Variable for the "checking_for_new_transaction" method
        sig = "Placeholder"
        # Function to execute in a separate thread
        def checking_for_new_transaction():
            nonlocal sig
            # Checking for new transaction
            sig = FindTxSignatures.find_transaction(tokenmysterybox, my_address)
        # Create a new thread and start it
        thread = threading.Thread(target=checking_for_new_transaction)
        thread.start()
        # Wait for the thread to complete or timeout after 5.5 seconds
        thread.join(timeout=5.5)
        # If the thread is still running after 5.5 seconds (timeout) or sig is "NoNewTransaction"
        if thread.is_alive() or sig == "NoNewTransaction":
            return "insufficient transaction amount"
        # If the next transaction after the user payment is the users refund transaction, i save it
        if sig == RPCResponse["result"]:
            first_record = tokenmysterybox.objects.first()
            first_record.transactions = sig
            first_record.save()
        return "insufficient transaction amount"
    # Save the necessary datas for later
    SIGNING_PUBKEY = signing_pubkey
    SIGNATURE = signature
    TRANSACTION_AMOUNT = transaction_amount
    return signature

# Second part of the token mystery box system.
def TokenMB_PaymentSystem2():
    global SIGNING_PUBKEY, TOKEN_ACCOUNT
    # Create token account for the buyer
    token_account = TokenMethods.TokenAccountCreator(SIGNING_PUBKEY)
    SIGNING_PUBKEY = 0
    TOKEN_ACCOUNT = token_account
    time.sleep(2)

# Third part of the token mystery box payment system.
def TokenMB_PaymentSystem3():
    # Wait for the create account transaction to get finalized status on the blockchain, 
    # because i can't mint tokens to an adress what don't "exists" yet
    time.sleep(9.9)

# Fourth part of the token mystery box payment system.
def TokenMB_PaymentSystem4(p2, p3, my_address):
    global TOKEN_ACCOUNT, SIGNATURE, TRANSACTION_AMOUNT, TACSIGNATURE, TOKENMINTERSIGNATURE, TOKENREWARDAMOUNT
    # Retrieve the first row from the database
    first_record = tokenmysterybox.objects.first()
    # Wait for the create account transaction
    time.sleep(3)
    # Mint the tokens to the buyer and change the necessary datas
    RPCResponse, token_reward_amount = TokenMethods.TokenMinter(TOKEN_ACCOUNT, TRANSACTION_AMOUNT, p2, p3)
    TOKEN_ACCOUNT = 0
    first_record.transactions = SIGNATURE
    first_record.save()
    TRANSACTION_AMOUNT = 0
    SIGNATURE = 0
    TokenMinterSignature = RPCResponse['result']
    # Variable for the "Checking_for_new_transaction" method
    TACsignature = "Placeholder"
    # Function to execute in a separate thread
    def Checking_for_new_transaction():
        nonlocal TACsignature
        # Checking for new transaction.
        TACsignature = FindTxSignatures.find_transaction(tokenmysterybox, my_address)
    # Create a new thread and start it
    thread = threading.Thread(target=Checking_for_new_transaction)
    thread.start()
    # Wait for the thread to complete or timeout after 6 seconds
    thread.join(timeout=6)
    # If the thread is still running after 6 seconds (timeout), or 
    # if the signature received from find_transaction is "NoNewTransaction"
    if thread.is_alive() or TACsignature == "NoNewTransaction":
        return "Congratulation", token_reward_amount
    TACSIGNATURE = TACsignature
    TOKENMINTERSIGNATURE = TokenMinterSignature
    TOKENREWARDAMOUNT = token_reward_amount
    return "--->"

# Fifth part of the token mystery box payment system. (Recomended)
def TokenMB_PaymentSystem5(my_address):
    global TACSIGNATURE, TOKENMINTERSIGNATURE, TOKENREWARDAMOUNT
    # Variable for the "Get_Transaction" method
    transaction_info = "Placeholder"
    # Function to execute in a separate thread
    def Get_Transaction():
        nonlocal transaction_info
        # Client for the blockchain.
        solana_client = Client(settings.SOLANA_API_URL)
        # Get more transaction info
        transaction_info = solana_client.get_transaction(tx_sig = TACSIGNATURE, commitment=Commitment("confirmed"))
    # Create a new thread and start it
    thread = threading.Thread(target=Get_Transaction)
    thread.start()
    # Wait for the thread to complete or timeout after 4.5 seconds
    thread.join(timeout=4.5)
    # If the thread is still running after 4.5 seconds (timeout), terminate the thread
    if thread.is_alive():
        return TOKENREWARDAMOUNT
    # Extracting the public key of the sender
    signing_pubkey = transaction_info["result"]["transaction"]["message"]["accountKeys"][0]
    # This indicates that this transaction is the token account creator transaction (With a height probability)
    if signing_pubkey == my_address:
        # Retrieve the first row from the database
        first_record = tokenmysterybox.objects.first()
        # Save the transaction signature of the token account creator transaction
        first_record.transactions = TACSIGNATURE
        first_record.save()
        TACSIGNATURE = 0
        # Variable for the "Checking_for_new_transaction" method
        TMsignature = "Placeholder"
        # Function to execute in a separate thread
        def Checking_for_new_transaction():
            nonlocal TMsignature
            # Checking for new transaction.
            TMsignature = FindTxSignatures.find_transaction(tokenmysterybox, my_address)
        # Create a new thread and start it
        thread = threading.Thread(target=Checking_for_new_transaction)
        thread.start()
        # Wait for the thread to complete or timeout after 6 seconds
        thread.join(timeout=6)
        # If the thread is still running after 6 seconds (timeout), or 
        # if the signature received from find_transaction is "NoNewTransaction"
        if thread.is_alive() or TMsignature == "NoNewTransaction":
            return TOKENREWARDAMOUNT
        # This indicates that this transaction is the token minting transaction
        if TMsignature == TOKENMINTERSIGNATURE:
            # Retrieve the first row from the database
            first_record = tokenmysterybox.objects.first()
            # Save the transaction signature of the token minting transaction
            first_record.transactions = TOKENMINTERSIGNATURE
            first_record.save()
            TOKENMINTERSIGNATURE = 0
        return TOKENREWARDAMOUNT
