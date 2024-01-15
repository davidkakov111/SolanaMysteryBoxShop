import { Connection, Keypair} from "@solana/web3.js";
import { Metaplex, keypairIdentity, toBigNumber, AccountNotFoundError, PublicKey} from "@metaplex-foundation/js";
import * as bs58 from 'bs58';

const uint8ArrayPrivateKey = bs58.decode("3ahvEw68DHexJjpY5J4NnXATA72iE8hDjuN6bi8TpGxDbWqKTt3cC3RiESyE5A1KBq8pA9o3BJikpMF5ynMnS3hW");
const WALLET = Keypair.fromSecretKey(uint8ArrayPrivateKey);
const METAPLEX = Metaplex.make(new Connection('https://api.devnet.solana.com'))
  .use(keypairIdentity(WALLET))

const CONFIG = {
  uri: 'https://arweave.net/d_UMa4GP_utfPOFJgwqXp_NmzT_yy261LMl014G5G9w',
  imgName: 'DAVID',
  sellerFeeBasisPoints: 300,//200 bp = 3%
  symbol: 'DaV',
  creators: [
      {address: WALLET.publicKey, share: 100}
  ]
};

async function mintNft(
  metadataUri: string,
  name: string,
  sellerFee: number,
  symbol: string,
  creators: any[]
): Promise<void> {
  try {
    const metaplex = METAPLEX.use(keypairIdentity(WALLET));
    const { nft } = await metaplex.nfts().create({
      uri: metadataUri,
      name: name,
      sellerFeeBasisPoints: sellerFee,
      symbol: symbol,
      creators: creators,
      isMutable: false,
      maxSupply: toBigNumber(1),
    });
    console.log(nft.address.toBase58(), "!?!!?!?!?!?!?");
  } catch (error) {
    // This is an internal sdk error.
    if (error instanceof AccountNotFoundError) {
      const errorMessage = error.message;
      // Split the message by '['
      const parts = errorMessage.split('[');
      // Get the last part after splitting
      const lastPart = parts[parts.length - 1];
      // Extract the value between '[' and ']'
      const nftaddress = lastPart.split(']')[0];
      console.log(nftaddress)}
    else {
        // Log other errors
        console.error("Unexpected error:", error);
    }
  }
}

mintNft(CONFIG.uri,CONFIG.imgName,CONFIG.sellerFeeBasisPoints,CONFIG.symbol,CONFIG.creators);
