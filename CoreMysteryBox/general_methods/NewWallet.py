# Imports
from solana.account import Account
from solana.keypair import Keypair
import base58

# New Solana wallet
def new_wallet():
    # Necesary datas
    account = Account()
    keypair = Keypair(account.secret_key())
    base58_private_key = base58.b58encode(keypair.secret_key).decode('utf-8')
    # Return the results
    return {
        "Byte private key for this program" : account.secret_key(),
        "Base 58 private key for phantom wallet" : base58_private_key,
        "Publik key" : keypair.public_key}
