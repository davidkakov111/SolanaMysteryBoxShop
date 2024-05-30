# Imports.
from solana.publickey import PublicKey
from CoreMysteryBox import settings
from spl.token.client import Token
from solana.keypair import Keypair
from solana.rpc.api import Client
import random

# Necesary datas.
client = Client(settings.SOLANA_API_URL)
program_id=PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')
owner_account = Keypair(settings.TokenMB_Privatekey)
# Token mint.
token_mint = Token(pubkey=PublicKey(settings.TokenMint),
    conn=client, program_id=program_id, payer=owner_account)

# Token account creator.
def TokenAccountCreator(recipent):
    try:
        # Create token account for the buyer, what is necesary for token mint
        tokacc = Token.create_account(skip_confirmation=True, self= token_mint, owner = PublicKey(recipent))
        return tokacc
    except Exception as e:
        raise e

# Token minter.
def TokenMinter(tokacc, txamount, p2, p3):
    try:
        txamount = float(txamount)
        # Mint the appropriate amount of tokens to the token account.
        if p2 > txamount:
            token_reward_amount = random.randint(1, 1e6)
            RPCResponse = Token.mint_to(self=token_mint, dest=PublicKey(tokacc), mint_authority=owner_account, 
                amount=token_reward_amount)
        elif p3 > txamount:
            token_reward_amount = random.randint(1e6, 1e9)
            RPCResponse = Token.mint_to(self=token_mint, dest=PublicKey(tokacc), mint_authority=owner_account, 
                amount=token_reward_amount)
        else:
            token_reward_amount = random.randint(1e9, 1e12)
            RPCResponse = Token.mint_to(self=token_mint, dest=PublicKey(tokacc), mint_authority=owner_account, 
                amount=token_reward_amount)
        return RPCResponse, token_reward_amount
    except Exception as e:
        raise e

# New token mint creator.
def CreateTokenMint():
    try:
        # Create a token mint
        mint = Token.create_mint(
            conn=client,
            payer=owner_account,
            mint_authority=owner_account.public_key,
            decimals=0,
            program_id=program_id
        )
    except Exception as e:
        raise e
    # Return the mint pubkey
    return mint.pubkey
