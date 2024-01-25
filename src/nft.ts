import { Connection, Keypair} from "@solana/web3.js";
import { Metaplex, keypairIdentity, toBigNumber, AccountNotFoundError, PublicKey} from "@metaplex-foundation/js";
import * as bs58 from 'bs58';
 
// Function for minting the NFT 
export async function mintNft(
  metadataUri: string,
  name: string,
  symbol: string,
  to: string,
  blockchain_endpoint: string,
  private_key: string
): Promise<string | unknown> {
  try {
    // Create keypair and metaplex instance with connection
    const uint8ArrayPrivateKey = bs58.decode(private_key);
    const WALLET = Keypair.fromSecretKey(uint8ArrayPrivateKey);
    const METAPLEX = Metaplex.make(new Connection(blockchain_endpoint))
    // With metaplex use my keypair
    const metaplex = METAPLEX.use(keypairIdentity(WALLET));
    // Create the NFT
    const { nft } = await metaplex.nfts().create({
      tokenOwner: new PublicKey(to),
      uri: metadataUri,
      name: name,
      symbol: symbol,
      sellerFeeBasisPoints: 300,
      creators: [{address: WALLET.publicKey, share: 100}],
      isMutable: false,
      maxSupply: toBigNumber(0),
    })
    // Return the NFT address 
    return nft.address.toBase58();
  } catch (error) {
    // This is an internal sdk error without real effect (This sdk is deprecated)
    if (error instanceof AccountNotFoundError) {
      const errorMessage = error.message;
      // Split the message by '['
      const parts = errorMessage.split('[');
      // Get the last part after splitting
      const lastPart = parts[parts.length - 1];
      // Extract the value between '[' and ']'
      const nftaddress = lastPart.split(']')[0];
      // Return the NFT address
      return nftaddress;
    }
    else {
      // If another error, return "error"
      return "error";
    }
  }
}
