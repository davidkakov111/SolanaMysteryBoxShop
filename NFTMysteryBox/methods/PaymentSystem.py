# Imports
from CoreMysteryBox.general_methods.FindValidPayment import FindValidPayment
from NFTMysteryBox.models import nftmysterybox
from NFTMysteryBox import NFT_Types
from CoreMysteryBox.settings import NFTMB_Privatekey
from . import metadataNFT, NFTApi
import json, threading

# Variables for temporary data storage (Faster then database calls)
IMAGE_URI = 0
METADATA_URI = 0
PAYMENT_DETAILS = 0
WORDS = []

# First part of the NFT Mystery Box payment system
def NFTMB_PaymentSystem1(my_address, puppy_price, cosmic_price, underwater_price, fantasy_price,
        ancient_price, botanical_price):
    global IMAGE_URI, METADATA_URI, PAYMENT_DETAILS, WORDS
    # Variables for the "payment_and_metadata" method
    tuple_result = "Placeholder"
    result = "Placeholder"
    # Function to execute in a separate thread
    def payment_and_metadata(database_table=nftmysterybox):
        nonlocal tuple_result, result
        # Check for a valid payment; if not found, return
        result = FindValidPayment(my_address, puppy_price, database_table, NFTMB_Privatekey)
        if type(result) != tuple:
            return result
        # From the transaction amount, determining the type of NFT to mint
        tx_amount = result[2]
        if tx_amount < cosmic_price:
            words = NFT_Types.puppy[1]
            word_type = NFT_Types.puppy[0]
        elif tx_amount < underwater_price:
            words = NFT_Types.cosmic[1]
            word_type = NFT_Types.cosmic[0]
        elif tx_amount < fantasy_price:
            words = NFT_Types.underwater[1]
            word_type = NFT_Types.underwater[0]
        elif tx_amount < ancient_price:
            words = NFT_Types.fantasy[1]
            word_type = NFT_Types.fantasy[0]
        elif tx_amount < botanical_price:
            words = NFT_Types.ancient[1]
            word_type = NFT_Types.ancient[0]
        else:
            words = NFT_Types.botanical[1]
            word_type = NFT_Types.botanical[0]
        # Complete NFT metadata creator method
        tuple_result = metadataNFT.main_NFTMetadata(words, word_type)
    # Create a new thread and start it
    thread = threading.Thread(target=payment_and_metadata)
    thread.start()
    # Wait for the thread to complete or timeout after 9.5 seconds
    thread.join(timeout=9.5)
    # If the thread is still running after 9.5 seconds (timeout), terminate the thread
    if thread.is_alive():
        return "timeout"
    if type(result) != tuple:
        return result
    if type(tuple_result) != tuple:
        return tuple_result
    # Save some data for later and then return
    IMAGE_URI = tuple_result[1]
    METADATA_URI = tuple_result[0]
    PAYMENT_DETAILS = result
    WORDS = [tuple_result[3], tuple_result[2]]
    return tuple_result[0]

# Second part of the NFT Mystery Box payment system
def NFTMB_PaymentSystem2():
    global METADATA_URI, PAYMENT_DETAILS, WORDS
    # Variable for the "NFT_Minting" method
    result = "Placeholder"
    # Function to execute in a separate thread
    def NFT_Minting():
        nonlocal result
        # Mint the NFT with my TS Solana NFT minter API
        result = NFTApi.MintNFT(uri=METADATA_URI, name=WORDS[1], symbol=WORDS[0], to=PAYMENT_DETAILS[1])
    # Create a new thread and start it
    thread = threading.Thread(target=NFT_Minting)
    thread.start()
    # Wait for the thread to complete or timeout after 9 seconds
    thread.join(timeout=9)
    # If the thread is still running after 9 seconds, terminate the thread 
    # and return 'Success' because the NFT was minted successfully anyway
    if thread.is_alive():
        # The NFT minting was successfull so I save the user payment
        first_record = nftmysterybox.objects.first()
        first_record.transactions = PAYMENT_DETAILS[0]
        first_record.save()
        return "Success"
    # If "NFTApi error", then return it
    if result == "NFTApi error":
        return result
    # If "error", then return "error" (this can come from the TS API code)
    if result != "timeout" and json.loads(result)['result'] == "error":
        return "error"
    # The NFT minting was successfull so I save the user payment
    first_record = nftmysterybox.objects.first()
    first_record.transactions = PAYMENT_DETAILS[0]
    first_record.save()
    # If there is a 'timeout' or not, return the 'IMAGE_URI' 
    # anyway because the NFT minting was successful
    if result == "timeout" or result != "timeout":
        return "Success"

# Third, an optional but recommended part of the NFT Mystery Box payment system
def NFTMB_PaymentSystem3(my_address, min_price):
    global IMAGE_URI
    try:
        # Check for a new transaction and save it if this was the NFT minting transaction
        FindValidPayment(my_address, min_price, nftmysterybox, NFTMB_Privatekey)
    except:
        pass
    # Return the NFT image
    return IMAGE_URI
