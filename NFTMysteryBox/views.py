# Imports
from CoreMysteryBox.general_methods import QRPay
from CoreMysteryBox import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .methods import PaymentSystem
from .models import nftmysterybox
from django.template import loader
from solana.keypair import Keypair
import requests, time

# My address variable
my_address = str(Keypair(settings.NFTMB_Privatekey).public_key)
# NFT Mystery Box price variables
puppy_price = 0.03
cosmic_price = 0.031
underwater_price = 0.032
fantasy_price = 0.033
ancient_price = 0.034
botanical_price = 0.035

# NFT mystery box view.
def NFT_mb(request):
    # Get the Solana price from the CoinGecko API and calculate the actual Mystery Box price.
    try:
        # Get the Solana price from the CoinGecko API.
        response = requests.get("https://api.coingecko.com/api/v3/simple/price", 
            params={"ids": "solana", "vs_currencies": "usd"}, timeout=8)
        # Raise error if the status code isn't 200 (OK)
        response.raise_for_status()
        # I retrieve the Solana price in Amarican Dollar.
        solana_data = response.json()
        solana_price_usd = int(solana_data["solana"]["usd"])
        # I calculate the price of each Mystery Box in USD. 
        puppy_Dollar = round(solana_price_usd * puppy_price, 2)
        cosmic_Dollar = round(solana_price_usd * cosmic_price, 2)
        underwater_Dollar = round(solana_price_usd * underwater_price, 2)
        fantasy_Dollar = round(solana_price_usd * fantasy_price, 2)
        ancient_Dollar = round(solana_price_usd * ancient_price, 2)
        botanical_Dollar = round(solana_price_usd * botanical_price, 2)
    except:
        # Formal error handing
        puppy_Dollar = "?"
        cosmic_Dollar = "?"
        underwater_Dollar = "?"
        fantasy_Dollar = "?"
        ancient_Dollar = "?"
        botanical_Dollar = "?"
    context = {
        "puppy_price": puppy_price,
        "puppy_Dollar": puppy_Dollar,
        "puppy_box_label": "Puppy Box",
        "cosmic_price": cosmic_price,
        "cosmic_Dollar": cosmic_Dollar,
        "cosmic_box_label": "Cosmic Box",
        "underwater_price": underwater_price,
        "underwater_Dollar": underwater_Dollar,
        "underwater_box_label": "Underwater Box",
        "fantasy_price": fantasy_price,
        "fantasy_Dollar": fantasy_Dollar,
        "fantasy_box_label": "Fantasy Box",
        "ancient_price": ancient_price,
        "ancient_Dollar": ancient_Dollar,
        "ancient_box_label": "Ancient Box",
        "botanical_price": botanical_price,
        "botanical_Dollar": botanical_Dollar,
        "botanical_box_label": "Botanical Box",
        }
    # Return after render the datas to the HTML template.
    template = loader.get_template("NFTMysteryBox/nft_mb.html")
    return HttpResponse(template.render(context, request))

# "SolPay" Qr code view for nft mystery boxes.
def NFTMB_GenerateQR(request,  box_label, box_price):
    try:
        # Get the Qr code.
        qr_code_data_url = QRPay.QRPay(recipent=my_address, amount=float(box_price), 
            qr_fill_color="darkblue", qr_bg_color="green", label=box_label)
    except:
        # Formal error handing
        qr_code_data_url = " "
    # Return after render the data to the HTML template
    return render(request, 'CoreMysteryBox/qr.html', {"qr": qr_code_data_url, 
        "no_copyright_txt": " ", "MB_PaymentView":"NFTMB-PV1", "MB_Learn": "learn-NFTMB"})

# Learn view for NFT Mystery Boxes
def learn_NFTMB(request):
    # Return and render the data to the HTML template
    return render(request, "NFTMysteryBox/NFTMB_response.html", 
        {"no_copyright_txt":" ", "learn":" "})

"""
N O T E :
I need to split my payment view into 3 parts (NFTMBPaymentView1, ..., NFTMBPaymentView3) 
because I can't use this view on Vercel for free if it runs for too long. I lock the 
first view to allow only one execution at a time and execute the views in a chained manner. 
To prevent anyone from interrupting the payment process by calling the other views, I 
secure them with a password (view_password). These passwords are only provided when they 
are run consecutively in sequence, so they cannot be run separately. The locking mechanism 
differs from typical approaches due to the unique nature of Vercel, a serverless 
environment. This approach is adapted to suit the constraints and capabilities of a 
serverless platform like Vercel.
"""
# View password variable
view_password = "No Password"
# Payment view 1.
def NFTMBPaymentView1(request):
    global view_password
    # Get the current time
    current_time = time.time()
    # Retrieve the first record from the database table along with the 'lock' and 'lock_time' fields
    first = nftmysterybox.objects.first()
    lock = first.lock
    lock_time = first.lock_time
    # If the lock is open or has been locked for more than 30 seconds, the payment view can run.
    # The timing is crucial because if the user abruptly terminates the view,
    # the lock may remain engaged, potentially resulting in a deadlock.
    if lock == "Open" or (current_time - lock_time > 30):
        # Lock the lock and update the lock time
        first.lock = "Close"
        first.lock_time = current_time
        first.save()
        try:
            # Search for new transaction, verify and create metadata for the NFT
            result = PaymentSystem.NFTMB_PaymentSystem1(my_address, 
                puppy_price, cosmic_price, underwater_price, fantasy_price,
                ancient_price, botanical_price)
            if result == "expected_test_error":
                1 / 0
        except:
            # Open the lock
            first = nftmysterybox.objects.first()
            first.lock = "Open"
            first.save()
            return render(request, "NFTMysteryBox/NFTMB_response.html", 
                {"text1":"There's an error in NFTMB_PaymentSystem1.", 
                "link1":"Try again", "payment_response":" ", "weakconnection":" "}) 
        if result in ("timeout", "NoNewTransaction", "NoValidTransaction", 
            "insufficient transaction amount", "Google error", "NFT Metadata error"):
            # Open the lock
            first = nftmysterybox.objects.first()
            first.lock = "Open"
            first.save()
        if result == "timeout":
            return render(request, "NFTMysteryBox/NFTMB_response.html", 
                {"text1":"The connection to the blockchain is weak", 
                "link1":"Try again", "weakconnection":" ", "payment_response":" "})
        elif result == "NoNewTransaction":
            return render(request, "NFTMysteryBox/NFTMB_response.html", 
                {"text1":"No payment has been received", "link1":"Try again", 
                "link2":"Learn More", "payment_response":" "}) 
        elif result == "NoValidTransaction":
            return render(request, "NFTMysteryBox/NFTMB_response.html", 
                {"text1":"No valid payment has been received", "link1":"Try again", 
                "link2":"Learn More", "payment_response":" "})
        elif result == "insufficient transaction amount":
            return render(request, "NFTMysteryBox/NFTMB_response.html", 
                {"text1":"The payment amount is insufficient, so it has been refunded to your wallet! Please don't change the payment amount!", 
                "link1":"Try again", "link2":"Learn More", "payment_response":" "})
        elif result == "Google error":
            return render(request, "NFTMysteryBox/NFTMB_response.html", 
                {"text1":"Can't find image", 
                "link1":"Try again", "weakconnection":" ", "payment_response":" "})
        elif result == "NFT Metadata error":
            return render(request, "NFTMysteryBox/NFTMB_response.html", 
                {"text1":"Failed to upload the NFT metadata", 
                "link1":"Try again", "weakconnection":" ", "payment_response":" "})
        else: # Success
            view_password = "NFTMBPaymentView2"
            # Next view...
            return redirect('NFTMB-PV2')
    else:
        return render(request, "NFTMysteryBox/NFTMB_response.html", 
            {"text1":"This payment is being processed. Please wait!", 
            "link1":"Try again", "link2":"Learn More", "payment_response":" "})
# Payment view 2.
def NFTMBPaymentView2(request):
    global view_password
    if view_password == "NFTMBPaymentView2":
        view_password = "No Password"
        try:
            response = PaymentSystem.NFTMB_PaymentSystem2()
            if response == "NFTApi error":
                # Open the lock
                first = nftmysterybox.objects.first()
                first.lock = "Open"
                first.save()
                return render(request, "NFTMysteryBox/NFTMB_response.html", 
                    {"text1":"Django NFT minting error", 
                    "link1":"Try again", "weakconnection":" ", "payment_response":" "})
            elif response == "error":
                # Open the lock
                first = nftmysterybox.objects.first()
                first.lock = "Open"
                first.save()
                return render(request, "NFTMysteryBox/NFTMB_response.html", 
                    {"text1":"TS NFT minting error", 
                    "link1":"Try again", "weakconnection":" ", "payment_response":" "})
            else:
                # In the next view, I will check for a new transaction after 
                # the user's payment. If it is the NFT minter transaction, 
                # I will then save it for a smoother user experience.
                view_password = "NFTMBPaymentView3"
                # Next view...
                return redirect('NFTMB-PV3')
        except:
            # Open the lock
            first = nftmysterybox.objects.first()
            first.lock = "Open"
            first.save()
            return render(request, "NFTMysteryBox/NFTMB_response.html", {
                "text1":"There's an error in NFTMBPaymentView2", 
                "link1":"Try again", "weakconnection":" ", "payment_response":" "})
    else:
        return render(request, "NFTMysteryBox/NFTMB_response.html", {"text1":"Wrong password for NFTMBPaymentView2", 
            "link1":"Try again", "link2":"Learn More", "payment_response":" "}) 
# Payment view 3.
def NFTMBPaymentView3(request):
    global view_password
    if view_password == "NFTMBPaymentView3":
        view_password = "No Password"
        try:
            img = PaymentSystem.NFTMB_PaymentSystem3(my_address, puppy_price)
            # Return the response with the NFT image
            return render(request, "NFTMysteryBox/NFTMB_response.html", {
                "text1":"🎉 Congratulations! 🎉",
                "text2": "Your NFT is now in your wallet! ",
                "NFT":img,
                "new":"🎁Unbox another NFT🎁",
                "payment_response":" "
            })
        except:
            return render(request, "NFTMysteryBox/NFTMB_response.html", {
                "text1":"🎉 Congratulations! 🎉",
                "text2": "Your NFT is now in your wallet!",
                "NFT":" ",
                "new":"🎁Unbox another NFT🎁",
                "payment_response":" "
            })
        finally:
            # Open the lock
            first = nftmysterybox.objects.first()
            first.lock = "Open"
            first.save()
    else:
        return render(request, "NFTMysteryBox/NFTMB_response.html", {"text1":"Wrong password for NFTMBPaymentView3", 
            "link1":"Try again", "link2":"Learn More", "payment_response":" "}) 
