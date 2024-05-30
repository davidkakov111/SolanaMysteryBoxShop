# Imports
from CoreMysteryBox.general_methods import QRPay
from solana.rpc.commitment import Commitment
from CoreMysteryBox import settings
from .methods import metadataNFT, NFTApi
from .models import nftmysterybox
from django.test import TestCase
from django.urls import reverse
from . import views, NFT_Types
import time, requests, json
from solana.rpc.api import Client

# Small views tests
class SmallViewsTests(TestCase):
    # Testing the NFT mystery box view
    def test_NFT_mb(self):
        # Simulate a GET request to the view and check the results
        response = self.client.get(reverse("NFTmb"))
        # Check that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Check the template
        self.assertTemplateUsed(response, "NFTMysteryBox/nft_mb.html")
        # Check whether the contextual data is as expected
        for data in ["puppy_price", "puppy_Dollar"]:
            self.assertTrue(isinstance(response.context[data], (int, float)))
        for label_key, label_value in {
            "puppy_box_label":"Puppy Box"
            }.items():
            self.assertEqual(response.context[label_key], label_value)
    # Testing the NFT mystery box QR code generator view
    def test_NFTMB_GenerateQR(self):
        Details_For_QRcodes = {
            "Puppy Box" : views.puppy_price
            }.items()
        for label, price in Details_For_QRcodes:
            # Get the Qr code
            qr_code_data_url = QRPay.QRPay(recipent=views.my_address, amount=float(price), 
                qr_fill_color="darkblue", qr_bg_color="green", label=label)
            # Simulate GET requests to the view
            response = self.client.get(reverse('NFTMB_generate_qr', args=[label, price]))
            # Check that the response has a status code of 200 (OK)
            self.assertEqual(response.status_code, 200)
            # Check the template
            self.assertTemplateUsed(response, "CoreMysteryBox/qr.html")
            # Check if the context data is as expected
            for key, value in {"qr": qr_code_data_url, "no_copyright_txt": " ", 
                "MB_PaymentView":"NFTMB-PV1", "MB_Learn": "learn-NFTMB"}.items():
                self.assertEqual(response.context[key], value)
    # Test the learn view for the NFT Mystery Boxes
    def test_learn_NFTMB(self):
        # Simulate GET requests to the view
        response = self.client.get(reverse('learn-NFTMB'))
        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Check the template
        self.assertTemplateUsed(response, "NFTMysteryBox/NFTMB_response.html")
        # Check if the response contains the expected content
        for key in ['no_copyright_txt', 'learn']:
            self.assertIn(key, response.context)

# Test the unique and critical components of the NFT Mystery Box payment system on devnet.
# (The common but critical components are tested in the CoreMysteryBox app test file.)
class PaymentViews(TestCase):
    # Payment views accessibility tests
    def test_payment_views_accessibility(self):
        payment_system_accessibility = {
            "Open": 0,
            "Close1": 31,
            "Close2": 0,
            'NFTMB-PV2': 'Wrong password for NFTMBPaymentView2', 
            'NFTMB-PV3': 'Wrong password for NFTMBPaymentView3',
        }
        # Check the accessibility of the payment system under various conditions
        for key, value in payment_system_accessibility.items():
            # If i test the TokenMBPaymentView1 accessibility
            if isinstance(value, int):
                # Creating the first object in the test database (test_TEST)
                nftmysterybox.objects.create(transactions = " ")
                # Retrieve the first record and save data to the database to 
                # test the view accessibility under various conditions
                first_record = nftmysterybox.objects.first()
                first_record.lock_time = time.time() - value
                if key == "Open":
                    first_record.lock = key
                else:
                    first_record.lock = "Close"
                first_record.save()
                url_name = 'NFTMB-PV1'
            else:
                url_name = key
            # Simulate GET requests to the view
            response = self.client.get(reverse(url_name))
            # Check if the response status code is 200 (OK)
            self.assertEqual(response.status_code, 200)
            # Check the template
            self.assertTemplateUsed(response, "NFTMysteryBox/NFTMB_response.html")
            # Check if the response contains the expected content
            if key == "Close2":
                text1_value = "This payment is being processed. Please wait!"
            elif key == "Close1" or key == "Open":
                """
                An anticipated error will arise due to certain sections of the view currently 
                configured to interact with the locally set TEST database, rather than the newly 
                created test_Test database generated by Django, which lacks essential values required
                to avoid triggering the error. This occurrence might be attributed to Django's 
                categorization of these sections differently compared to others within the test. 
                Nevertheless, this setup facilitates the testing of the 'outer' aspects of the view,
                emphasizing the assessment of the locking system, which is pivotal in this test.
                If I encounter this error, it indicates that the 'view_lock' is functioning as expected!
                """
                text1_value = "There's an error in NFTMB_PaymentSystem1."
            else:
                text1_value = value
            for KEY, VALUE in {"text1":text1_value, 
                "link1":"Try again"}.items():
                self.assertEqual(response.context[KEY], VALUE)
    # Test the "check_image_accessibility" method
    def test_image_accessibility(self):
        # The first is an inaccessible image, and the second is not
        for img, boolean in {
            "https://www.facebook.com/photo/?fbid=483037603868461&set=a.483037577201797" : False, 
            "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Cat_August_2010-4.jpg/1200px-Cat_August_2010-4.jpg" : True
            }.items():
            result = metadataNFT.check_image_accessibility(img)
            self.assertEqual(boolean, result)
    # Test the "google_image_search" method
    def test_google_image_search(self):
        img_link, key_word = metadataNFT.google_image_search(NFT_Types.puppy[1], NFT_Types.puppy[0])
        boolean = metadataNFT.check_image_accessibility(img_link)
        self.assertEqual(boolean, True)
        self.assertIn(key_word, NFT_Types.puppy[1])
    # Test the 'NFT_metadata' method for uploading metadata to GitHub
    def test_NFT_metadata(self):
        # Create and upload the metadata to GitHub
        uri = metadataNFT.NFT_metadata(
            name="Name",
            symbol="Na",
            description="Place holder",
            img_link="https://something.com",
            webshop_link="https://webshop.com"
        )
        # Make a get request to the NFT metadata
        response = requests.get(uri)
        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Check the content type
        self.assertEqual(response.headers['Content-Type'], 'text/plain; charset=utf-8')
        # Expected NFT metadata
        metadata  = {
            "name": "Name",
            "symbol": "Na",
            "description": "Place holder",
            "image": "https://something.com",
            "external_url": "https://webshop.com"
            }
        # Check the actual content
        self.assertEqual(response.json(), metadata)
    # Test the NFT minting system using the 'MintNFT' method, which makes 
    # an API call to my TypeScript code what actually mint the NFT
    def test_MintNFT(self):
        # Inactive Solana wallet public key
        pubkey = "2wW4Qvp2ATk9pcWy5oqqMfnWp1QWquGKvM3j3ecS8scM"
        # Solana blockchain api
        client = Client(settings.SOLANA_API_URL)
        # Retrieve the latest transaction signature for this pubkey
        latest_signature_before = client.get_signatures_for_address(account=pubkey, limit=1, commitment=Commitment("confirmed")).get('result')[0].get('signature')
        # Mint an NFT to a given address
        result = NFTApi.MintNFT(
            "https://raw.githubusercontent.com/davidkakov111/NFTMetadata/main/nft_metadata_20240121171638.json",
            "Ruby Bengal Cat",
            "Puppy",
            pubkey
            )
        # Check for error
        self.assertNotEqual(result, "NFTApi error")
        if result != "timeout":
            self.assertNotEqual(json.loads(result)['result'], "error")
        # Retrieve the latest transaction signature for this pubkey, after the NFT minting
        latest_signature_after = client.get_signatures_for_address(account=pubkey, limit=1, commitment=Commitment("confirmed")).get('result')[0].get('signature')
        # Check for new transaction (NFT minting transaction)
        self.assertNotEqual(latest_signature_before, latest_signature_after)
