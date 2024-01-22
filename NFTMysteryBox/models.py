from django.db import models

# Model for NFT Mystery Boxes
class nftmysterybox (models.Model):
    transactions = models.CharField(max_length=300, default=" ")
    transactions_with_same_block_time = models.CharField(max_length=300, default=" ")
    block_time = models.IntegerField(default=0)
    lock = models.CharField(max_length=5, default="Open")
    lock_time = models.IntegerField(default=0)
