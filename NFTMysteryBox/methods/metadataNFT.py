# Imports
import requests, random, json, base64, datetime
from typing import Tuple
from PIL import Image
from io import BytesIO
import PIL, os
from pathlib import Path
from dotenv import load_dotenv
# Load the .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Method for checking the accessibility of an image
def check_image_accessibility(image_url):
    try:
        # Send a get request to the image link 
        response = requests.get(image_url, timeout=2)
        # Open it
        image = Image.open(BytesIO(response.content))
        # Accessible image
        return True
    except (requests.RequestException, OSError, PIL.UnidentifiedImageError):
        # Inaccessible image
        return False

# Method for Image Search
def google_image_search(words: Tuple[str, ...], word_type):
    """
    I need to check the accessibility of the images because 
    sometimes Google provides image URLs from platforms 
    like Instagram, Facebook... These images can't be loaded 
    as NFTs because they require login credentials so i filter them out.
    """
    # Base URL for Google searching
    base_url = "https://www.googleapis.com/customsearch/v1"
    # Loop until get an accessible image, or up to 10
    for i in range(10):
        try:
            # Select a random word from words
            word = random.choice(words)
            # Params for searching
            params = {
                "key": os.getenv('gcs_api_key'),
                "cx": os.getenv('gcs_cx'),
                "q": word + " " + word_type,
                "searchType": "image",
                "num": 1,
            }
            # Search for image with get request
            response = requests.get(base_url, params=params, timeout=2)
            # Extract the image link
            result = response.json().get("items")[0].get('link')
            # Check the accessibility of the image link
            accessible = check_image_accessibility(result)
            # If accessible return the "result" and "word"
            if accessible:
                return result, word
        except:
            accessible = False
    # If something goes wrong, return 'Google error' with "?"
    return "Google error", "?"

# Method for NFT metadata building and saving 
def NFT_metadata(name: str, symbol: str, description: str, img_link: str, webshop_link: str):
    try:
        # NFT metadata structure
        metadata  = {
            "name": name,
            "symbol": symbol,
            "description": description,
            "image": img_link,
            "external_url": webshop_link
            }
        # Convert metadata to JSON
        metadata_json = json.dumps(metadata)
        # My repo path
        repo = 'davidkakov111/NFTMetadata'
        # Generate a unique filename based on the current timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f'nft_metadata_{timestamp}.json'
        # Upload the "metadata_json" to the specified location on Github ("filename")
        result = requests.put(
            f'https://api.github.com/repos/{repo}/contents/{filename}',
            headers = {
                'Authorization': f'Token {os.getenv('github_api_token')}'
            },
            json = {
                "message": "New NFT metadata",
                "content": base64.b64encode(metadata_json.encode()).decode(),
                "branch": "main"
            }
        )
        # Extract the NFT metadata uri and return it
        uri = result.json()["content"]["download_url"]
        return uri
    except:
        return "NFT Metadata error"

# Complete NFT metadata creator method
def main_NFTMetadata(words, word_type):
    # Search for image link with Google
    image_link, key_word = google_image_search(words=words, word_type=word_type)
    # If can't get the image, then return "Google error"
    if image_link == "Google error":
        return image_link
    # Build and save the NFT metadata
    uri = NFT_metadata(
        name=key_word, 
        symbol=word_type, 
        description="NFT from the revolutionary Solana Mystery Box shop!",
        img_link=image_link,
        webshop_link="https://solanamysterybox.vercel.app/"
        )
    # If the metadata upload failed, return "NFT Metadata error"
    if uri == "NFT Metadata error":
        return uri
    # Return the results in a tuple
    return (uri, image_link, key_word, word_type)
