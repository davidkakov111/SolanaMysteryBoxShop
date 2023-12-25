# Imports 
from CoreMysteryBox.general_methods import FindTxSignatures, SolanaTransfer
from SolanaMysteryBox.models import solanamysterybox
from solana.rpc.commitment import Commitment
from solana.publickey import PublicKey
from CoreMysteryBox import settings
from solana.keypair import Keypair
from solana.rpc.api import Client
import threading, time, random

# My solana mystery box pubkey
my_address = str(Keypair(settings.SolanaMB_Privatekey).public_key)

# Solana Mystery Box payment system 
def SolanaMB_PaymentSystem(common_price, epic_price, legendary_price):
    # Variable for the "Checking_for_new_transaction" method
    signature = "Placeholder"
    # Function to execute in a separate thread
    def Checking_for_new_transaction():
        nonlocal signature
        # Checking for new transaction.
        try:
            signature = FindTxSignatures.find_transaction(solanamysterybox, my_address)
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
    # If the received signature is "NoNewTransaction", return it
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
    # Verifying the correctness of the transaction
    if transaction_amount <= 0 or recipent_pubkey != my_address:
        # Retrieve the first row from the database
        first_record = solanamysterybox.objects.first()
        first_record.transactions = signature
        first_record.save()
        return "NoValidTransaction"
    # If the amount is insufficient, I transfer back the 
    # amount - expected fee to the buyer if positive
    if transaction_amount < common_price:
        # Extract the fee.
        fee = transaction_info["result"]["meta"]["fee"]
        # Extract the transaction amount - fee (In lamports)
        txAmount = (postbalance - prebalance)-fee
        if txAmount <= 0:
            # Retrieve the first row from the database
            first_record = solanamysterybox.objects.first()
            first_record.transactions = signature
            first_record.save()
            return "NoValidTransaction"
        # Send back the transaction amount.
        RPCResponse = SolanaTransfer.Solana_transfer(
            sender_privatekey=settings.SolanaMB_Privatekey,
            recipient_pubkey=PublicKey(signing_pubkey), 
            amount=txAmount)
        # Retrieve the first row from the database
        first_record = solanamysterybox.objects.first()
        first_record.transactions = signature
        first_record.save()
        time.sleep(2) # Wait for the solana transfer transaction to get at least "confirmed" status
        # Variable for the "checking_for_new_transaction" method
        sig = "Placeholder"
        # Function to execute in a separate thread
        def checking_for_new_transaction():
            nonlocal sig
            # Checking for new transaction
            sig = FindTxSignatures.find_transaction(solanamysterybox, my_address)
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
            first_record = solanamysterybox.objects.first()
            first_record.transactions = sig
            first_record.save()
        return "insufficient transaction amount"
    # Randomly calculate the reward for the buyer:
    # If the user pay for the common solana mystery box:
    if transaction_amount < epic_price:
        revards_in_lamports = [1, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7]
        random_reward_in_lamports = int(random.choice(revards_in_lamports))
    # If the user pay for the epic solana mystery box:
    elif transaction_amount < legendary_price:
        revards_in_lamports = [5, 5e1, 5e2, 5e3, 5e4, 5e5, 5e6, 5e7, 5e8]
        random_reward_in_lamports = int(random.choice(revards_in_lamports))
    # If the user pay for the legendary solana mystery box:
    else:
        revards_in_lamports = [1, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9]
        random_reward_in_lamports = int(random.choice(revards_in_lamports))
    # Distribute the reward
    RPCResponse = SolanaTransfer.Solana_transfer(
        sender_privatekey=settings.SolanaMB_Privatekey,
        recipient_pubkey=PublicKey(signing_pubkey), 
        amount=random_reward_in_lamports)
    # Retrieve the first row from the database
    first_record = solanamysterybox.objects.first()
    first_record.transactions = signature
    first_record.save()
    time.sleep(2) # Wait for the solana transfer transaction to get at least "confirmed" status
    # Variable for the "checking_for_new_transaction" method
    sig = "Placeholder"
    # Function to execute in a separate thread
    def checking_for_new_transaction():
        nonlocal sig
        # Checking for new transaction
        sig = FindTxSignatures.find_transaction(solanamysterybox, my_address)
    # Create a new thread and start it
    thread = threading.Thread(target=checking_for_new_transaction)
    thread.start()
    # Wait for the thread to complete or timeout after 5.5 seconds
    thread.join(timeout=5.5)
    # Calculate the reward in solana
    random_reward_in_solana = ("{:.9f}".format(random_reward_in_lamports / 1e9)).rstrip('0').rstrip('.')
    # Set the JackPot variable to True if the user hit the heighest reward
    if random_reward_in_lamports == revards_in_lamports[-1]:
        JackPot = True
    else:
        JackPot = False
    # If the thread is still running after 5.5 seconds (timeout) or sig is "NoNewTransaction"
    if thread.is_alive() or sig == "NoNewTransaction":
        return [random_reward_in_solana, JackPot]
    # If the next transaction after the user's payment is the user's reward transaction, I save it.
    if sig == RPCResponse["result"]:
        first_record = solanamysterybox.objects.first()
        first_record.transactions = sig
        first_record.save()
    return [random_reward_in_solana, JackPot]
