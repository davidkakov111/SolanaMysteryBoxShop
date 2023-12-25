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
        for privatekey in [settings.TokenMB_Privatekey, settings.SolanaMB_Privatekey]:
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
        tokenmysterybox.objects.create(block_time=1701460972)
        # Retrieving the first record to save data into it, for testing the 
        # 'find_transaction()' method in a specific critical scenario too
        first_record = tokenmysterybox.objects.first()
        first_record.transactions = "5KBSTnRjpEc4pbXgQmpC1AmVthko5c5VFKG7zVHkrQssFS9ZkQeJWK9WCEsFRnvjZRCBKTUgyJwigLUshANxAzNH"
        first_record.transactions_with_same_block_time = "3m1ncPQQxebuPwJpmXKbokMX6WJ23vagwJVhdrHHtc3xJmD8MrbmEEDsZY9eRkCqoJPG9PVSu6dXifubo6vhzBuQ"
        first_record.save()
        """
        Here two signatures (second and third) share the same block time, potentially leading to an endless loop.
        The 'find_transaction' method is designed to handle such cases, retrieving transactions in a specific order.
        """ 
        # Expected new transactions in the correct order
        expected_transactions = [
            "3m1ncPQQxebuPwJpmXKbokMX6WJ23vagwJVhdrHHtc3xJmD8MrbmEEDsZY9eRkCqoJPG9PVSu6dXifubo6vhzBuQ",
            "2NSF5kuDvdQBCc5hK5yGuABW4h3ajF5BP8jEey6ggiBAdj5ojeST1bkSzQj8YJa6JZRkoPji4L5yCQCS8obFfXfd", # Same     time
            "38ZG9VYixct35bNJPF4Gviq4ay1jodPBo1hzLiMaa9o7JfdABkuucBYmR72QVXRo4gG4uXrYXpewd6UUj2Q4ie3g", #     block
            "5Mubu3L4Gm9jHSuEHMEz8QdF6hesGhLWbGe2DLJNY52pBo54fZoxY8suMsBPhfAbJe1RVscpYMWWYe2cJnd3pr2y",
            "5Xz6Wz6paSrRTS63CHr963KMzgDvdmr43fj3UNnHo8vrzxFe8QWbqGgMF8NH21VUSv6bEhHM7w7nwskWXt2wbrmR"
        ]
        for expected_transaction in expected_transactions:
            # Checking for new transaction
            new_transaction : str = find_transaction(tokenmysterybox, 
                address="BbpydPo6NmWP4gfboT6eL1G5a56kZF9DnszHxkSsvHRZ")
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
