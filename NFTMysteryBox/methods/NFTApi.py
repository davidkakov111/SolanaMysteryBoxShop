# Imports
import requests, base58
from CoreMysteryBox import privatedatas, settings
from solana.keypair import Keypair

# Mint the Solana NFT with my TS API
def MintNFT(uri, name, symbol, to):
    try:
        # Convert the byte private key to Base58, as this is the required format for the TS API
        base58_private_key = base58.b58encode(
            Keypair(settings.NFTMB_Privatekey).secret_key).decode('utf-8')
        # Data for the NFT
        data = {
            "uri":uri,
            "name":name,
            "symbol":symbol,
            "to":to,
            "blockchain_endpoint":settings.SOLANA_API_URL,
            "private_key":base58_private_key
        }
        """
        The NFT creator API is hosted on Vercel, a serverless environment, 
        which may cause the 'cold start' phenomenon, leading to a 504 
        status code; however, the NFT is still created successfully.
        """
        # Call the API
        response = requests.post(
            url=privatedatas.nft_api, 
            json=data, 
            headers={'authorization': privatedatas.nft_api_key}
        )
        # Return "timeout" if the status code is 504, if not, return the response
        if response.status_code == 504:
            return "timeout"
        else:
            return response.text
    except:
        # If something goes wrong, return "NFTApi error"
        return "NFTApi error"
