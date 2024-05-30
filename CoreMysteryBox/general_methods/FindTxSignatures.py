# Imports
from typing import Optional, List, Dict
from solana.publickey import PublicKey
from solana.rpc.commitment import Commitment
from solana.rpc.api import Client
from solana.transaction import TransactionSignature
from CoreMysteryBox import settings

# Find transaction signatures.
def find_transaction_signatures(reference: PublicKey, until: Optional[TransactionSignature] = None, commitment: Commitment = None):
    try: 
        # Solana blockchain api
        client = Client(settings.SOLANA_API_URL)
        # Retrieve the new signatures
        signatures = client.get_signatures_for_address(account=reference, until=until, commitment=commitment).get('result')
    except:
        signatures = "NoNewTransaction"
    if signatures == []:
        signatures = "NoNewTransaction"
    return signatures

# Find transaction signature or signatures by block time
def find_transactions_by_block_time(old_transaction, blocktime, database_table, address):
    # Find at least confirmed transactions for my_adress, back in time until old_transaction
    SIGNATURES = find_transaction_signatures(
        reference=address,
        until=old_transaction,
        commitment=Commitment("confirmed")
        )
    # If not found new transaction
    if SIGNATURES == "NoNewTransaction":
        return SIGNATURES, "?"
    # Retrieve the minimum blockTime value from these new transactions
    min_blocktime = SIGNATURES[-1]['blockTime']
    # Retrieve the signature(s) associated with this min_blocktime
    Signatures : List[Dict] = [dct for dct in SIGNATURES if dct['blockTime'] == min_blocktime]
    # Add the signatures to this list from the dictionaires
    signatures_list : List[str] = [sig['signature'] for sig in Signatures]
    # If the new transaction(s) have the same block time as the old transaction
    if min_blocktime == blocktime:
        # Retrieve from the database the transaction(s) that have already been saved and proceed, in a list
        values_of_column = database_table.objects.values_list('transactions_with_same_block_time', flat=True)
        # Add the signature(s) to this list if they are not in the database
        signatures : List[str] = [signature for signature in signatures_list if signature not in values_of_column]
        # If there are no new transactions that haven't been processed with the same block time as the 'old_transaction'
        if signatures == []:
            # Put the new transaction(s) to this list after the "min_blocktime"
            signatures_new_list : List[Dict] = [dct for dct in SIGNATURES if dct not in Signatures]
            # If no new transaction
            if signatures_new_list == []:
                return "NoNewTransaction", "?"
            # Get the latest block time from these new transaction(s)
            new_min_blocktime = signatures_new_list[-1]['blockTime']
            # Retrieve the signature(s) associated with this new_min_blocktime
            sign : List[Dict] = [dct for dct in signatures_new_list if dct['blockTime'] == new_min_blocktime]
            # Add the signatures to this list from the dictionaires
            SignatureS : List[str] = [i['signature'] for i in sign]
            # Return this signature(s) and the associated minimum block time
            return SignatureS, new_min_blocktime
        # Return this signature(s) and the associated minimum block time
        return signatures, min_blocktime
    # Return this signature(s) and the associated minimum block time
    return signatures_list, min_blocktime

# Find transaction signature
def find_transaction(database_table, address):
    first_record = database_table.objects.first()
    # Get the "old" transaction
    old_saved_signature = first_record.transactions
    # Retrieve the values of the 'transactions_with_same_block_time' column
    values_of_column = database_table.objects.values_list('transactions_with_same_block_time', flat=True)
    # If the old_saved_signature is not in the values_of_column
    if old_saved_signature not in values_of_column:
        # Get the first signature from the 'transactions_with_same_block_time' column
        sign = first_record.transactions_with_same_block_time
    # If the old_saved_signature is in the values_of_column
    else:
        # Retrieve the ID (primary key) of the 'old_saved_signature' from the 'transactions_with_same_block_time' column
        id_of_the_match = database_table.objects.get(transactions_with_same_block_time=old_saved_signature).pk
        try :
            # Retrieve the second signature after the old one in the 'transactions_with_same_block_time' column
            next_id = id_of_the_match + 1
            sign = database_table.objects.get(id=next_id).transactions_with_same_block_time
        except:
            sign = " "
    # If a new transaction with the same block time has been saved in the database
    if sign != " ":
        return sign
    # Get the previous block time
    blocktime = first_record.block_time
    # Retrieve the new transaction(s) from the blockchain
    signature_list, min_blocktime = find_transactions_by_block_time(
        old_transaction=old_saved_signature,
        blocktime=blocktime,
        database_table=database_table,
        address=address
        )
    # If not found new transaction
    if signature_list == "NoNewTransaction":
        # Return "NoNewTransaction"
        return signature_list
    # Create a list that will contain the signature that I should return
    for_return = []
    for_return.append(signature_list[0])
    # If the new transaction(s) have a different block time than the old one(s)
    if min_blocktime != blocktime:
        # Number of row(s) in the database table
        num_rows = database_table.objects.count()
        num_rows -= 1 # Because I don't want to delete the first row (object) from the table
        for i in range(num_rows):
            database_table.objects.latest('id').delete()
        # Update the necessary fields
        first_record.transactions_with_same_block_time = signature_list.pop(0)
        first_record.block_time = min_blocktime
        # Save the changes
        first_record.save()
    # If the signature_list isn't empty after deleting the first element 
    # in the previous 'if' condition by using pop
    if signature_list != []:
        # Save the signature(s)
        for signature in signature_list:
            database_table.objects.create(transactions_with_same_block_time = signature)
    # Return the signature
    return for_return[0]
