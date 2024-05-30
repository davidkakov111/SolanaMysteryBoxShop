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
import time, threading

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
        """
        In the "expected_transactions" two signatures (second and third) will share the same block time, 
        potentially leading to an endless loop. The 'find_transaction' method is designed to 
        handle such cases, retrieving transactions in a specific order.
        """ 
        expected_transactions = []
        # Function for sending solana transaction
        def Send(amount: int):
            RPCResponse : dict = SolanaTransfer.Solana_transfer(
                sender_privatekey=settings.SolanaMB_Privatekey,
                recipient_pubkey=PublicKey("8MrLVuny1kHyKifNBCNk3r9uanYVFLKKanFdRwp5g9po"), 
                amount=amount)
            expected_transactions.append(RPCResponse["result"])
        # Send the first transaction
        Send(100)
        # Creating the first record in the "test_Test" database
        tokenmysterybox.objects.create(transactions = "", transactions_with_same_block_time = expected_transactions[0])
        # Wait for the next solana block
        time.sleep(0.5)
        thread1 = threading.Thread(target=Send, args=([100]))
        thread2 = threading.Thread(target=Send, args=([101])) # I can't send multiple similar transactions at once due to blockchain behavior.
        thread1.start()
        thread2.start()
        thread2.join()
        # Wait for the next solana block
        time.sleep(0.5)
        # Send the last transaction
        Send(100)
        for index in range(len(expected_transactions)):
            # Checking for new transaction
            new_transaction : str = find_transaction(tokenmysterybox, 
                address="8MrLVuny1kHyKifNBCNk3r9uanYVFLKKanFdRwp5g9po")
            # Save the new_transaction (pretending that this has been processed)
            first_record = tokenmysterybox.objects.first()
            first_record.transactions = new_transaction
            first_record.save()
            # Verify if the new transaction matches the expected transaction
            if 1 <= index <= 2:
                self.assertIn(container=[expected_transactions[1], expected_transactions[2]], member=new_transaction)
            else:
                self.assertEqual(new_transaction, expected_transactions[index])

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
