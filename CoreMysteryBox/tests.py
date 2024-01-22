# Imports
from CoreMysteryBox.general_methods.FindTxSignatures import find_transaction
from CoreMysteryBox.general_methods import SolanaTransfer
from TokenMysteryBox.models import tokenmysterybox
from django.test import TestCase, override_settings
from CoreMysteryBox import settings
from solana.keypair import Keypair
from solana.rpc.api import Client
from solana.publickey import PublicKey
from .general_methods import NewWallet
from django.urls import reverse

# Small views tests
class SmallViewsTests(TestCase):
    # Testing the index / home view
    def test_index(self):
        # Simulate a GET request to the view
        response = self.client.get(reverse("home"))
        # Check that the response has a status code of 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Check the template
        self.assertTemplateUsed(response, "CoreMysteryBox/index.html")
    # Testing the handler404 view with turned off DEBUG
    @override_settings(DEBUG = False)
    def test_handler404(self):
        # Simulate a GET request to an non existing url
        response = self.client.get('/non-existent-url/')
        # Check that the response has a status code of 200 (OK) instead 404 in this case
        self.assertEqual(response.status_code, 200)
        # Check the template
        self.assertTemplateUsed(response, "CoreMysteryBox/handler404.html")

# Test the common but critical Solana methods
class GeneralSolanaMethods(TestCase):
    # Test the functionality of the 'new_wallet' method
    def test_new_wallet(self):
        # Create new Solana wallet
        new_wallet_details : dict = NewWallet.new_wallet()
        # Check the new_wallet_details
        for detail in [
            (new_wallet_details["Base 58 private key for phantom wallet"], str),
            (new_wallet_details["Byte private key for this program"], bytes),
            (new_wallet_details["Publik key"] , PublicKey)
            ]:
            self.assertIsInstance(detail[0], detail[1])
    # Test the functionality of the "Solana_transfer" method
    def test_Solana_transfer(self):
        for privatekey in [settings.TokenMB_Privatekey, settings.SolanaMB_Privatekey, settings.NFTMB_Privatekey]:
            # Try to request an airdrop, however, there's a limit, I can't always obtain airdrops
            try:
                Client(settings.SOLANA_API_URL).request_airdrop(str(Keypair(privatekey).public_key), int(1e9))
            except:
                pass
            # Send Solana lamports to a pubkey
            RPCResponse : dict = SolanaTransfer.Solana_transfer(
                sender_privatekey=privatekey,
                recipient_pubkey=PublicKey("6u6Zm2uQUjZCAaN8cc2TC9wgwVvBTVozC7a9SQqbh8Se"), 
                amount=100)
            # Check the RPCResponse
            self.assertTrue(isinstance(RPCResponse["result"], str))
    # Test the functionality of the "find_transaction()" method
    def test_find_transaction(self):
        # Creating the first object in the "test_Test" database
        tokenmysterybox.objects.create(block_time=0)
        # Retrieving the first record to save data into it, for testing the 
        # 'find_transaction()' method in a specific critical scenario too
        first_record = tokenmysterybox.objects.first()
        first_record.transactions = "5R2PjkNUpPqM3Kpzk8VVFB3JQA5czbLh26Ziq34Ush3A7jvAG6eCPA8yCRuXR6auFyFJyU2QbVEjTEAbapm1iGN5"
        first_record.transactions_with_same_block_time = "2w9MVzs5qSrejCBk5ato75xVWUXmgETdc15YiEMyj8DgVzqE3A3JwtHmhTBg6oM9NnJhfA86CYHBHkQ9YQoPm9jf"
        first_record.save()
        """
        Here two signatures (second and third) share the same block time, potentially leading to an endless loop.
        The 'find_transaction' method is designed to handle such cases, retrieving transactions in a specific order.
        """ 
        # Expected new transactions in the correct order
        expected_transactions = [
            "2w9MVzs5qSrejCBk5ato75xVWUXmgETdc15YiEMyj8DgVzqE3A3JwtHmhTBg6oM9NnJhfA86CYHBHkQ9YQoPm9jf",
            "2dw4j1C29f8Gv7TUghTJWi9gxJMw6wRYa4Raw7rBdPBV2YZv8ndHJK2QGdtuoUKssbi9TUFoxE5jJPH9GL6RDgNA", # Same     time
            "3fk1CLfczsBBvnpKKJPwcvrvf5UcTfmvrXuQTgP2qwPMh2WVLZEaJc5Qg8THFKqrUmarvsFr5avwJ61FR3RScXrf", #     block
            "PE9eWt9kdtrakhtQT4a63r1ihgYaz82Xezy68UzQrgvWcHaU5DzmQF55EuT3CGgAZJEihEx7BBuiKV4J6Vqmpdd"
        ]
        for expected_transaction in expected_transactions:
            # Checking for new transaction
            new_transaction : str = find_transaction(tokenmysterybox, 
                address="8MrLVuny1kHyKifNBCNk3r9uanYVFLKKanFdRwp5g9po")
            # Save the new_transaction (pretending that this has been processed)
            first_record = tokenmysterybox.objects.first()
            first_record.transactions = new_transaction
            first_record.save()
            # Verify if the new transaction matches the expected transaction
            self.assertEqual(new_transaction, expected_transaction)

# Local database test
class DatabaseTest(TestCase):
    # First inserting values, querying and testing it, after overriding, querying and testing it
    def test_Database(self):
        # Inserting values
        data = {
            "transactions": "ABC" * 100,
            "transactions_with_same_block_time": "ACB" * 100,
            "block_time": 100,
            "lock_time": 100,
            "lock": "ABCDE",
        }
        tokenmysterybox.objects.create(**data)
        # Querying and Testing
        transactions = tokenmysterybox.objects.get(transactions=data["transactions"])
        for key, value in data.items():
            self.assertEqual(getattr(transactions, key), value)
        # Overriding
        new_data = {
            "transactions": "abc" * 55,
            "transactions_with_same_block_time": "acb" * 56,
            "lock": "ba" * 2 + "d",
            "block_time": 17,
            "lock_time": 16,
        }
        latest_record = tokenmysterybox.objects.latest('id')
        for key, value in new_data.items():
            setattr(latest_record, key, value)
        latest_record.save()
        # Querying and Testing after overriding
        transactions = tokenmysterybox.objects.get(transactions=new_data["transactions"])
        for key, value in new_data.items():
            self.assertEqual(getattr(transactions, key), value)
