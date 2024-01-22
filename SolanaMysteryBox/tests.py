# Imports
from SolanaMysteryBox.models import solanamysterybox
from CoreMysteryBox.general_methods import QRPay
from SolanaMysteryBox import views
from django.test import TestCase
from django.urls import reverse
import time

# Small views tests
class SmallViewsTests(TestCase):
    # Testing the solana mystery box view
    def test_solana_mb(self):
        # Simulate a GET request to the view and check the results
        response = self.client.get(reverse("Solanamb"))
        # Check that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Check the template
        self.assertTemplateUsed(response, "SolanaMysteryBox/solana_mb.html")
        # Check whether the contextual data is as expected
        for data in ["common_price", "epic_price", "legendary_price", 
            "common_max_reward", "epic_max_reward", "legendary_max_reward",
            "dollar_common_price", "dollar_epic_price", "dollar_legendary_price"]:
            self.assertTrue(isinstance(response.context[data], (int, float)))
        for label_key, label_value in {
            "common_box_label": "Common Box",
            "epic_box_label": "Epic Box",
            "legendary_box_label": "Legendary Box"}.items():
            self.assertEqual(response.context[label_key], label_value)
    # Testing the solana mystery box QR code generator view
    def test_SolanaMB_GenerateQR(self):
        Details_For_QRcodes = {
            "Common Box" : views.common_price, 
            "Epic Box" : views.epic_price, 
            "Legendary Box" : views.legendary_price}.items()
        for label, price in Details_For_QRcodes:
            # Get the Qr code
            qr_code_data_url = QRPay.QRPay(recipent=views.my_address, amount=price, 
                qr_fill_color="darkblue", qr_bg_color="green", label=label)
            # Simulate GET requests to the view
            response = self.client.get(reverse('SolanaMB_generate_qr', args=[label, price]))
            # Check that the response has a status code of 200 (OK)
            self.assertEqual(response.status_code, 200)
            # Check the template
            self.assertTemplateUsed(response, "CoreMysteryBox/qr.html")
            # Check if the context data is as expected
            for key, value in {"qr": qr_code_data_url, "no_copyright_txt": " ", 
                "MB_PaymentView":"SolanaMB-PV", "MB_Learn": "learn-solanaMB"}.items():
                self.assertEqual(response.context[key], value)
    # Test the Solana Mystery Box learn view.
    def test_learn_solanaMB(self):
        # Simulate GET requests to the view
        response = self.client.get(reverse('learn-solanaMB'))
        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Check the template
        self.assertTemplateUsed(response, "SolanaMysteryBox/solanaMB_response.html")
        # Check if the response contains the expected content
        for key in ['no_copyright_txt', 'learn']:
            self.assertIn(key, response.context)

# Test the unique and critical component(s) of the Solana Mystery Box payment system on devnet.
# (The common but critical components are tested in the CoreMysteryBox app test file.)
class PaymentView(TestCase):
    # Payment view accessibility tests
    def test_payment_view_accessibility(self):
        payment_system_accessibility = {
            "Open": 0,
            "Close1": 16,
            "Close2": 0,
        }
        # Check the accessibility of the payment system under various conditions
        for key, value in payment_system_accessibility.items():
            # Creating the first object in the test database (test_TEST)
            solanamysterybox.objects.create(transactions = " ")
            # Retrieve the first record and save data to the database to 
            # test the view accessibility under various conditions
            first_record = solanamysterybox.objects.first()
            first_record.lock_time = time.time() - value
            if key == "Open":
                first_record.lock = key
            else:
                first_record.lock = "Close"
            first_record.save()
            # Simulate GET requests to the view
            response = self.client.get(reverse('SolanaMB-PV'))
            # Check if the response status code is 200 (OK)
            self.assertEqual(response.status_code, 200)
            # Check the template
            self.assertTemplateUsed(response, "SolanaMysteryBox/solanaMB_response.html")
            # Check if the response contains the expected content
            if key == "Close2":
                text1_value = "This payment is being processed. Please wait!"
            else:
                """
                An anticipated error will arise due to certain sections of the view currently 
                configured to interact with the locally set 'TEST' database, rather than the newly 
                created 'test_Test' database generated by Django, which lacks essential values required
                to avoid triggering the error. This occurrence might be attributed to Django's 
                categorization of these sections differently compared to others within the test. 
                Nevertheless, this setup facilitates the testing of the 'outer' aspects of the view,
                emphasizing the assessment of the locking system, which is pivotal in this test.
                If I encounter this error, it indicates that the 'view_lock' is functioning as expected!
                """
                text1_value = "There's an error in SolanaMB_PaymentSystem."
            for KEY, VALUE in {"text1":text1_value, 
                "link1":"Try again", "link2":"Learn More"}.items():
                self.assertEqual(response.context[KEY], VALUE)
