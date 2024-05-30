# Imports.
from solana.system_program import TransferParams, transfer
from solana.transaction import Transaction
from solana.publickey import PublicKey
from CoreMysteryBox import settings
from solana.keypair import Keypair
from solana.rpc.api import Client

# Solana transaction builder and sender.
def Solana_transfer(sender_privatekey: bytes, recipient_pubkey: PublicKey, amount: int):
    try:
        client = Client(settings.SOLANA_API_URL)
        # Initialize sender account.
        sender = Keypair.from_seed(bytes(sender_privatekey))
        # Get the recent blockhash.
        rbh = client.get_recent_blockhash()["result"]["value"]["blockhash"]
        # Create a Solana transaction.
        txn = Transaction(recent_blockhash=rbh).add(transfer(TransferParams(
            from_pubkey=sender.public_key, to_pubkey=recipient_pubkey, lamports=amount)))
        # Sign the transaction.
        txn.sign(sender)
        # Send the transaction.
        RPCResponse = client.send_transaction(txn, sender)
        return RPCResponse
    except Exception as e: 
        raise e
