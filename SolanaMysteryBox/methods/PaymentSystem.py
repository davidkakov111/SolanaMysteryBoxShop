# Imports 
from CoreMysteryBox.general_methods import FindTxSignatures, SolanaTransfer, FindValidPayment
from SolanaMysteryBox.models import solanamysterybox
from solana.publickey import PublicKey
from CoreMysteryBox import settings
from solana.keypair import Keypair
import threading, time, random

# My solana mystery box pubkey
my_address = str(Keypair(settings.SolanaMB_Privatekey).public_key)

# Solana Mystery Box payment system 
def SolanaMB_PaymentSystem(common_price, epic_price, legendary_price):
    # Find valid payment
    result = FindValidPayment.FindValidPayment(my_address, common_price, solanamysterybox, settings.SolanaMB_Privatekey)
    # If not found valid payment, return the exact response
    if type(result) != tuple:
        return result
    # Get the transaction amount from the result
    transaction_amount = result[2]
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
        recipient_pubkey=PublicKey(result[1]), 
        amount=random_reward_in_lamports)
    # Retrieve the first row from the database
    first_record = solanamysterybox.objects.first()
    first_record.transactions = result[0]
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
