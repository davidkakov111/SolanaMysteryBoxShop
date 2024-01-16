import { NextApiRequest, NextApiResponse } from 'next';
import { mintNft } from '../../src/nft';

// Api handler
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Only POST allowed
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method Not Allowed' });
  }
  // Comparing the API key
  const apiKey = req.headers.authorization;
  if (apiKey !== 'cnieh57t85gsk494i0gd%689ijuhdy#4%$dfuvuvty6nd') {
    return res.status(401).json({ message: 'Unauthorized' });
  }
  // Mint the NFT to the provided pubkey
  const requestData = req.body;
  const result = await mintNft(requestData.uri,requestData.name,requestData.symbol,requestData.to)
  // Return the result, what can be the NFT address or "error"
  return res.status(200).json({result: result});
}
