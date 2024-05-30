# Imports
from CoreMysteryBox.general_methods import QRPay
from solana.rpc.commitment import Commitment
from .models import tokenmysterybox
from solana.publickey import PublicKey
from CoreMysteryBox import settings
from .methods import TokenMethods
from solana.rpc.api import Client
from django.test import TestCase
from django.urls import reverse
from . import views
import time

# Small views tests
class SmallViewsTests(TestCase):
    # Testing the token mystery box view
    def test_token_mb(self):
        # Simulate a GET request to the view and check the results
        response = self.client.get(reverse("Tokenmb"))
        # Check that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Check the template
        self.assertTemplateUsed(response, "TokenMysteryBox/token_mb.html")
        # Check whether the contextual data is as expected
        for data in ["Dollar1", "Dollar2", "Dollar3", "p1", "p2", "p3"]:
            self.assertTrue(isinstance(response.context[data], (int, float)))
        for label_key, label_value in {
            "common_box_label": "Common Box",
            "epic_box_label": "Epic Box",
            "legendary_box_label": "Legendary Box"}.items():
            self.assertEqual(response.context[label_key], label_value)
    # Testing the token mystery box QR code generator view
    def test_TokenMB_GenerateQR(self):
        Details_For_QRcodes = {
            "Common Box" : views.price1, 
            "Epic Box" : views.price2, 
            "Legendary Box" : views.price3}.items()
        for label, price in Details_For_QRcodes:
            # Get the Qr code
            qr_code_data_url = QRPay.QRPay(recipent=views.my_address, amount=price, 
                qr_fill_color="darkblue", qr_bg_color="green", label=label)
            # Simulate GET requests to the view
            response = self.client.get(reverse('TokenMB_generate_qr', args=[label, price]))
            # Check that the response has a status code of 200 (OK)
            self.assertEqual(response.status_code, 200)
            # Check the template
            self.assertTemplateUsed(response, "CoreMysteryBox/qr.html")
            # Check if the context data is as expected
            for key, value in {"qr": qr_code_data_url, "no_copyright_txt": " ", 
                "MB_PaymentView":"TokenMB-PV1", "MB_Learn": "learn-tokenMB"}.items():
                self.assertEqual(response.context[key], value)
    # Test the learn view for token Mystery Boxes.
    def test_learn_tokenMB(self):
        # Simulate GET requests to the view
        response = self.client.get(reverse('learn-tokenMB'))
        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Check the template
        self.assertTemplateUsed(response, "TokenMysteryBox/tokenMB_response.html")
        # Check if the response contains the expected content
        for key in ['no_copyright_txt', 'title']:
            self.assertIn(key, response.context)

# Test the unique and critical components of the Token Mystery Box payment system on the devnet.
# (The common but critical components are tested in the CoreMysteryBox app test file.)
class PaymentViews(TestCase):
    # Payment views accessibility tests
    def test_payment_views_accessibility(self):
        payment_system_accessibility = {
            "Open": 0,
            "Close1": 41,
            "Close2": 0,
            'TokenMB-PV2': 'Wrong password for TokenMBPaymentView2', 
            'TokenMB-PV3': 'Wrong password for TokenMBPaymentView3', 
            'TokenMB-PV4': 'Wrong password for TokenMBPaymentView4',
            'TokenMB-PV5': 'Wrong password for TokenMBPaymentView5'
        }
        # Check the accessibility of the payment system under various conditions
        for key, value in payment_system_accessibility.items():
            # If i test the TokenMBPaymentView1 accessibility
            if isinstance(value, int):
                # Creating the first object in the test database (test_TEST)
                tokenmysterybox.objects.create(transactions = " ")
                # Retrieve the first record and save data to the database to 
                # test the view accessibility under various conditions
                first_record = tokenmysterybox.objects.first()
                first_record.lock_time = time.time() - value
                if key == "Open":
                    first_record.lock = key
                else:
                    first_record.lock = "Close"
                first_record.save()
                url_name = 'TokenMB-PV1'
            else:
                url_name = key
            # Simulate GET requests to the view
            response = self.client.get(reverse(url_name))
            # Check if the response status code is 200 (OK)
            self.assertEqual(response.status_code, 200)
            # Check the template
            self.assertTemplateUsed(response, "TokenMysteryBox/tokenMB_response.html")
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
                text1_value = "There's an error in TokenMB_PaymentSystem1."
            else:
                text1_value = value
            for KEY, VALUE in {"text1":text1_value, 
                "link1":"Try again", "link2":"Learn More"}.items():
                self.assertEqual(response.context[KEY], VALUE)

    # Test the functionality of the "TokenAccountCreator" method in conjunction with the "CreateTokenMint" method
    def test_TokenAccountCreator_and_CreateTokenMint(self):
        for method in [
            TokenMethods.TokenAccountCreator("Hv3TTCtKSuJVq19WPzaMD1VFDn9eRvVELoBqkdbt6LVz"),
            TokenMethods.CreateTokenMint()]:
            # Call the method, and check the pubkey
            self.assertIsInstance(method, PublicKey)

    # Test the functionality of the 'TokenMinter' method in conjunction with the 'get_transaction' method
    def test_TokenMinter_and_get_transaction(self):
        for price, reward_range in {
            views.price1: [1, 1e6], 
            views.price2: [1e6, 1e9], 
            views.price3: [1e9, 1e12]}.items():
            # Destination token account for token minting
            dest_mint_address = "8SXEyVXJVbHGbCvGCw9RiKpF92ssdKxY5KvqFDfdaxk1"
            # Mint the tokens
            RPCResponse, reward = TokenMethods.TokenMinter(tokacc=dest_mint_address, 
                txamount=price, p2=views.price2, p3=views.price3)
            # Waiting for the mint transaction to reach at least confirmed status on the blockchain
            time.sleep(2)
            # Get transaction information about the mint transaction
            transaction_info : dict = Client(settings.SOLANA_API_URL).get_transaction(
                tx_sig=RPCResponse["result"], commitment=Commitment("confirmed"))
            # Extracting the number of minted tokens
            post_token_ballance = transaction_info["result"]["meta"]["postTokenBalances"][0]["uiTokenAmount"]["amount"]
            pre_token_ballance = transaction_info["result"]["meta"]["preTokenBalances"][0]["uiTokenAmount"]["amount"]
            nr_of_minted_tokens = int(post_token_ballance) - int(pre_token_ballance)
            # Extracting the recipent
            recipent = transaction_info["result"]["transaction"]["message"]["accountKeys"][2]
            # Extracting the instruction type
            instruction_type = transaction_info["result"]["meta"]["logMessages"][1]
            # Extracting the used token program
            used_token_program = transaction_info["result"]["meta"]["logMessages"][3]
            # Conditions to check the mint transaction validity
            conditions = {
                nr_of_minted_tokens:reward_range, 
                recipent:dest_mint_address,
                instruction_type:"Program log: Instruction: MintTo",
                used_token_program:"Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success"
                }
            # Checking the mint transaction validity
            for key, value in conditions.items():
                if key == nr_of_minted_tokens:
                    self.assertTrue(value[0] <= key <= value[1])
                    self.assertTrue(key, reward)
                else:
                    self.assertEqual(key, value)
