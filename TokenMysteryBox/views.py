# Imports
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from CoreMysteryBox.general_methods import QRPay
from .methods import PaymentSystem
from .models import tokenmysterybox
from CoreMysteryBox import settings
from solana.keypair import Keypair
import requests, time

# My address variable
my_address = str(Keypair(settings.TokenMB_Privatekey).public_key)
# Price variables
price1 = 0.05
price2 = 0.2
price3 = 0.4

# Token mystery box view.
def token_mb (request):
    # Get the Solana price from the CoinGecko API and calculate the actual Mystery Box prices.
    try:
        # Get the Solana price from the CoinGecko API.
        response = requests.get("https://api.coingecko.com/api/v3/simple/price", 
            params={"ids": "solana", "vs_currencies": "usd"}, timeout=8)
        # Raise error if the status code isn't 200 (OK)
        response.raise_for_status()
        # Retrieve the Solana price in Amarican Dollar.
        solana_data = response.json()
        solana_price_usd = int(solana_data["solana"]["usd"])
        # Calculate the price of each Mystery Box in USD. 
        Dollar1 = round(solana_price_usd * price1, 2)
        Dollar2 = round(solana_price_usd * price2, 2)
        Dollar3 = round(solana_price_usd * price3, 2)
    except:
        # Formal error handing
        Dollar1 = "?"
        Dollar2 = "?"
        Dollar3 = "?"
    context = {"p1": price1, "p2": price2, "p3": price3, 
        "Dollar1":Dollar1, "Dollar2":Dollar2, "Dollar3":Dollar3,
        "common_box_label": "Common Box",
        "epic_box_label": "Epic Box",
        "legendary_box_label": "Legendary Box"
        }
    # Return after render the datas to the HTML template.
    template = loader.get_template("TokenMysteryBox/token_mb.html")
    return HttpResponse(template.render(context, request))

# "SolPay" Qr code view for token mystery boxes.
def TokenMB_GenerateQR (request,  box_label, box_price):
    try:
        # Get the Qr code.
        qr_code_data_url = QRPay.QRPay(recipent=my_address, amount=float(box_price), 
            qr_fill_color="darkblue", qr_bg_color="green", label=box_label)
    except:
        # Formal error handing
        qr_code_data_url = " "
    # Return after render the data to the HTML template.
    return render(request, 'CoreMysteryBox/qr.html', {"qr": qr_code_data_url, 
        "MB_PaymentView":"TokenMB-PV1", "MB_Learn": "learn-tokenMB", "no_copyright_txt": " "})

# Learn view for token Mystery Boxes.
def learn_tokenMB (request):
    # Return after render the data to the HTML template.
    return render(request, "TokenMysteryBox/tokenMB_response.html", {"no_copyright_txt":" ",
        "title":"Payment process"})

"""
N O T E :
I need to split my payment view into 5 parts (TokenMBPaymentView1, TokenMBPaymentView2, 
TokenMBPaymentView3, TokenMBPaymentView4, TokenMBPaymentView5) because I can't use this 
view on Vercel for free if it runs for too long. I lock the first view to allow only one 
execution at a time and execute the views in a chained manner. To prevent anyone from 
interrupting the payment process by calling the other views, I secure them with a password 
(view_password). These passwords are only provided when they are run consecutively in 
sequence, so they cannot be run separately. The locking mechanism differs from typical 
approaches like Caching-Based Locking due to the unique nature of Vercel, a serverless 
environment. This approach is adapted to suit the constraints and capabilities of a 
serverless platform like Vercel.
"""
# View password variable
view_password = "No Password"
# Payment view 1.
def TokenMBPaymentView1(request):
    global view_password
    # Get the current time
    current_time = time.time()
    # Retrieve the first record from the database table along with the 'lock' and 'lock_time' fields
    first = tokenmysterybox.objects.first()
    lock = first.lock
    lock_time = first.lock_time
    # If the lock is open or has been locked for more than 40 seconds, the payment view can run.
    # The timing is crucial because if the user abruptly terminates the view,
    # the lock may remain engaged, potentially resulting in a deadlock.
    if lock == "Open" or (current_time - lock_time > 40):
        # Lock the lock and update the lock time
        first.lock = "Close"
        first.lock_time = current_time
        first.save()
        try:
            # Search for new transaction and verify
            result = PaymentSystem.TokenMB_PaymentSystem1(my_address=my_address, price1=price1)
            if result == "expected_test_error":
                1 / 0
        except:
            # Open the lock
            first = tokenmysterybox.objects.first()
            first.lock = "Open"
            first.save()
            return render(request, "TokenMysteryBox/tokenMB_response.html", 
                {"text1":"There's an error in TokenMB_PaymentSystem1.", "link1":"Try again", "link2":"Learn More"}) 
        if result in ("timeout", "NoNewTransaction", "NoValidTransaction", "insufficient transaction amount"):
            # Open the lock
            first = tokenmysterybox.objects.first()
            first.lock = "Open"
            first.save()
        if result == "timeout":
            return render(request, "TokenMysteryBox/tokenMB_response.html", 
                {"text1":"The connection to the blockchain is weak", "link1":"Try again", "weakconnection":" "})
        elif result == "NoNewTransaction":
            return render(request, "TokenMysteryBox/tokenMB_response.html", 
                {"text1":"No payment has been received", "link1":"Try again", "link2":"Learn More"}) 
        elif result == "NoValidTransaction":
            return render(request, "TokenMysteryBox/tokenMB_response.html", 
                {"text1":"No valid payment has been received", "link1":"Try again", "link2":"Learn More"})
        elif result == "insufficient transaction amount":
            return render(request, "TokenMysteryBox/tokenMB_response.html", 
                {"text1":"The payment amount is insufficient, so it has been refunded to your wallet! Please don't change the payment amount!", 
                    "link1":"Try again", "link2":"Learn More"})
        elif result == "Already created token account":
            view_password = "TokenMBPaymentView3"
            # Third view...
            return redirect('TokenMB-PV3')
        else: # Successful payment
            view_password = "TokenMBPaymentView2"
            # Next view...
            return redirect('TokenMB-PV2')
    else:
        return render(request, "TokenMysteryBox/tokenMB_response.html", 
            {"text1":"This payment is being processed. Please wait!", "link1":"Try again", "link2":"Learn More"})
# Payment view 2.
def TokenMBPaymentView2(request):
    global view_password
    if view_password == "TokenMBPaymentView2":
        view_password = "No Password"
        try:
            # Creating token account for the buyer
            PaymentSystem.TokenMB_PaymentSystem2()
            view_password = "TokenMBPaymentView3"
            # Next view...
            return redirect('TokenMB-PV3')
        except:
            # Open the lock
            first = tokenmysterybox.objects.first()
            first.lock = "Open"
            first.save()
            return render(request, "TokenMysteryBox/tokenMB_response.html", 
                {"text1":"There's an error in TokenMBPaymentView2.", "link1":"Try again", "link2":"Learn More"}) 
    else:
        return render(request, "TokenMysteryBox/tokenMB_response.html", 
            {"text1":"Wrong password for TokenMBPaymentView2", "link1":"Try again", "link2":"Learn More"}) 
# Payment view 3.
def TokenMBPaymentView3(request):
    global view_password
    if view_password == "TokenMBPaymentView3":
        view_password = "No Password"
        # Here, only sleep happens, i can't sleep directly from the view, because then Vercel skipp it
        PaymentSystem.TokenMB_PaymentSystem3()
        view_password = "TokenMBPaymentView4"
        # Next view...
        return redirect('TokenMB-PV4')
    else:
        return render(request, "TokenMysteryBox/tokenMB_response.html", 
            {"text1":"Wrong password for TokenMBPaymentView3", "link1":"Try again", "link2":"Learn More"}) 
# Payment view 4.
def TokenMBPaymentView4(request):
    global view_password
    if view_password == "TokenMBPaymentView4":
        view_password = "No Password"
        try:
            # Mint the tokens to the token accont.
            PaymentSystem.TokenMB_PaymentSystem4(price2, price3)        
            view_password = "TokenMBPaymentView5"
            # Next view...
            return redirect('TokenMB-PV5')
        except:
            # Open the lock
            first = tokenmysterybox.objects.first()
            first.lock = "Open"
            first.save()
            return render(request, "TokenMysteryBox/tokenMB_response.html", 
                {"text1":"There's an error in TokenMBPaymentView4.", "link1":"Try again", "link2":"Learn More"})
    else:
        return render(request, "TokenMysteryBox/tokenMB_response.html", 
            {"text1":"Wrong password for TokenMBPaymentView4", "link1":"Try again", "link2":"Learn More"}) 
# Payment view 5.
def TokenMBPaymentView5(request):
    global view_password
    if view_password == "TokenMBPaymentView5":
        view_password = "No Password"
        try:
            # Save any additional data that is recommended for a smoother user experience
            TOKENREWARDAMOUNT = PaymentSystem.TokenMB_PaymentSystem5(my_address, price1)
            return render(request, "TokenMysteryBox/tokenMB_response.html", {
                "text1":"🎉🎉🎉Congratulations🎉🎉🎉", 
                "text2":f"🔍You have received {TOKENREWARDAMOUNT:,.0f} Tokens🔍", 
                "new":"🔮Discover New Boxes🎁"
            })
        except:
            return render(request, "TokenMysteryBox/tokenMB_response.html", {
                "text1":"There's an error in TokenMBPaymentView5", 
                "text2":"🔍But you have received the Tokens🔍", 
                "new":"🔮Discover New Boxes🎁"
            })
        finally:
            # Open the lock
            first = tokenmysterybox.objects.first()
            first.lock = "Open"
            first.save()
    else:
        return render(request, "TokenMysteryBox/tokenMB_response.html", 
            {"text1":"Wrong password for TokenMBPaymentView5", "link1":"Try again", "link2":"Learn More"}) 
