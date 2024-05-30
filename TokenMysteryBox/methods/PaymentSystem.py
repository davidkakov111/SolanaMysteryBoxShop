# Imports
from CoreMysteryBox import settings
from CoreMysteryBox.general_methods import FindTxSignatures, FindValidPayment
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
TOKENMINTERSIGNATURE = 0
TOKENREWARDAMOUNT = 0

# First part of the token mystery box payment system.
def TokenMB_PaymentSystem1(my_address, price1):
    global SIGNING_PUBKEY, SIGNATURE, TRANSACTION_AMOUNT, TOKEN_ACCOUNT
    # Find valid payment
    result = FindValidPayment.FindValidPayment(my_address, price1, tokenmysterybox, settings.TokenMB_Privatekey)
    # If not found valid payment, return the exact response
    if type(result) != tuple:
        return result
    # data from the result
    signature = result[0]
    transaction_amount = result[2]
    # If there is a token account, then return, because there is 
    # no need to create a new one for this payment again.
    # (This can occur if the view abruptly terminates within a 
    # given time by the user, such as navigating away or something similar)
    if TOKEN_ACCOUNT != 0:
        SIGNATURE = signature
        TRANSACTION_AMOUNT = transaction_amount
        return "Already created token account"
    # Save the necessary datas for later
    SIGNING_PUBKEY = result[1]
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
def TokenMB_PaymentSystem4(p2, p3):
    global TOKEN_ACCOUNT, SIGNATURE, TRANSACTION_AMOUNT, TOKENMINTERSIGNATURE, TOKENREWARDAMOUNT
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
    TOKENMINTERSIGNATURE = RPCResponse['result']
    TOKENREWARDAMOUNT = token_reward_amount

# Fifth part of the token mystery box payment system. (Recomended)
def TokenMB_PaymentSystem5(my_address, min_price):
    global TOKENMINTERSIGNATURE, TOKENREWARDAMOUNT
    try:
        # Save the token for account creation transaction
        FindValidPayment.FindValidPayment(my_address, min_price, tokenmysterybox, settings.TokenMB_Privatekey)
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
    except:
        return TOKENREWARDAMOUNT
