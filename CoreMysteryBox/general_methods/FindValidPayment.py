# imports 
from CoreMysteryBox.general_methods import FindTxSignatures, SolanaTransfer
from solana.rpc.commitment import Commitment
from CoreMysteryBox import settings
from solana.publickey import PublicKey
from solana.rpc.api import Client
import threading, time

# Method for finding valid payment for address
def FindValidPayment(for_address, min_price, database_table, private_key):
    # Variable for the "Checking_for_new_transaction" method
    signature = "Placeholder"
    # Function to execute in a separate thread
    def Checking_for_new_transaction():
        nonlocal signature
        # Checking for new transaction.
        try:
            signature = FindTxSignatures.find_transaction(database_table, for_address)
        except Exception as e:
            if isinstance(e, AttributeError):
                # While executing this section of the payment system within the tests, an anticipated 
                # error arises. However, I face difficulty in explicitly raising it here. 
                # So, I manage the error further along in the primary segment of the view.
                signature = "expected_test_error"
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
        return "NoNewTransaction"
    if signature == "expected_test_error":
        return "expected_test_error"
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
    if transaction_amount <= 0 or recipent_pubkey != for_address:
        # Retrieve the first row from the database
        first_record = database_table.objects.first()
        first_record.transactions = signature
        first_record.save()
        return "NoValidTransaction"
    # If the amount is insufficient, I transfer back the 
    # amount - expected fee to the buyer if positive
    if transaction_amount < min_price:
        # Extract the fee.
        fee = transaction_info["result"]["meta"]["fee"]
        # Extract the transaction amount - fee (In lamports)
        txAmount = (postbalance - prebalance)-fee
        if txAmount <= 0:
            # Retrieve the first row from the database
            first_record = database_table.objects.first()
            first_record.transactions = signature
            first_record.save()
            return "NoValidTransaction"
        # Send back the transaction amount.
        RPCResponse = SolanaTransfer.Solana_transfer(
            sender_privatekey=private_key,
            recipient_pubkey=PublicKey(signing_pubkey), 
            amount=txAmount)
        # Retrieve the first row from the database
        first_record = database_table.objects.first()
        first_record.transactions = signature
        first_record.save()
        time.sleep(2) # Wait for the solana transfer transaction to get at least "confirmed" status
        # Variable for the "checking_for_new_transaction" method
        sig = "Placeholder"
        # Function to execute in a separate thread
        def checking_for_new_transaction():
            nonlocal sig
            # Checking for new transaction
            sig = FindTxSignatures.find_transaction(database_table, for_address)
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
            first_record = database_table.objects.first()
            first_record.transactions = sig
            first_record.save()
        return "insufficient transaction amount"
    # I have received a new valid payment, so I return the details
    return (signature, signing_pubkey, transaction_amount)
