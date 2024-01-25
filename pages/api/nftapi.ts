import { NextApiRequest, NextApiResponse } from 'next';
import { mintNft } from '../../src/nft';

// Api handler
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Only POST allowed
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method Not Allowed! (Use POST!)' });
  }
  // Comparing the API key
  const apiKey = req.headers.authorization;
  if (apiKey !== 'Non public :)') {
    return res.status(401).json({ message: 'Unauthorized!' });
  }
  // Mint the NFT to the provided pubkey
  const requestData = req.body;
  const result = await mintNft(requestData.uri,requestData.name,requestData.symbol,requestData.to,requestData.blockchain_endpoint,requestData.private_key)
  // Return the result, what can be the NFT address or "error"
  return res.status(200).json({result: result});
}
