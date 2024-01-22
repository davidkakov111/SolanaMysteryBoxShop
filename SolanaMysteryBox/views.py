# Imports
from CoreMysteryBox.general_methods import QRPay
from CoreMysteryBox import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from solana.keypair import Keypair
from .methods import PaymentSystem
from .decorators import payment_lock
import requests

# My address variable
my_address = str(Keypair(settings.SolanaMB_Privatekey).public_key)
# Price variables
common_price = 0.0015
epic_price = 0.07
legendary_price = 0.15
# Max reward variables
common_max_reward = 0.01
epic_max_reward = 0.5
legendary_max_reward = 1

# Solana mystery box view.
def solana_mb (request):
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
        dollar_common_price = round(solana_price_usd * common_price, 2)
        dollar_epic_price = round(solana_price_usd * epic_price, 2)
        dollar_legendary_price = round(solana_price_usd * legendary_price, 2)
    except:
        # Formal error handing
        dollar_common_price="?"
        dollar_epic_price="?"
        dollar_legendary_price="?"
    # Context for return
    context = {
        "common_price": common_price, 
        "epic_price": epic_price, 
        "legendary_price": legendary_price, 
        "common_max_reward":common_max_reward,
        "epic_max_reward":epic_max_reward,
        "legendary_max_reward":legendary_max_reward,
        "dollar_common_price":dollar_common_price, 
        "dollar_epic_price":dollar_epic_price, 
        "dollar_legendary_price":dollar_legendary_price,
        "common_box_label": "Common Box",
        "epic_box_label": "Epic Box",
        "legendary_box_label": "Legendary Box",
        }
    # Return after render the context to the HTML template.
    template = loader.get_template("SolanaMysteryBox/solana_mb.html")
    return HttpResponse(template.render(context, request))

# "SolPay" Qr code view for solana mystery boxes.
def SolanaMB_GenerateQR (request,  box_label, box_price):
    try:
        # Get the Qr code.
        qr_code_data_url = QRPay.QRPay(recipent=my_address, amount=float(box_price), 
            qr_fill_color="darkblue", qr_bg_color="green", label=box_label)
    except:
        # Formal error handing
        qr_code_data_url = " "
    # Return after render the datas to the HTML template.
    return render(request, 'CoreMysteryBox/qr.html', {"qr": qr_code_data_url, "no_copyright_txt": " ",
        "MB_PaymentView":"SolanaMB-PV", "MB_Learn": "learn-solanaMB"})

# Learn view for solana mystery boxes.
def learn_solanaMB (request):
    # Return after render the datas to the HTML template.
    return render(request, "SolanaMysteryBox/solanaMB_response.html", {"no_copyright_txt":" ", "learn":" "})

"""
N O T E :
I lock the payment view with "payment_lock" decorator to allow only one execution at a time. 
The locking mechanism differs from typical approaches like Caching-Based Locking due 
to the unique nature of Vercel, a serverless environment. This approach is adapted 
to suit the constraints and capabilities of a serverless platform like Vercel.
"""
# Solana Mystery Box payment view.
@payment_lock
def SolanaMBPaymentView(request):
    try:
        # Search for new transaction and verify
        result = PaymentSystem.SolanaMB_PaymentSystem(common_price, epic_price, legendary_price)
        if result == "expected_test_error":
            1 / 0 # Zero division error
    except:
        return render(request, "SolanaMysteryBox/solanaMB_response.html", {"payment_response":" ",
            "text1":"There's an error in SolanaMB_PaymentSystem.", "link1":"Try again", "link2":"Learn More"}) 
    if result == "timeout":
        return render(request, "SolanaMysteryBox/solanaMB_response.html", {"payment_response":" ",
            "text1":"The connection to the blockchain is weak", "link1":"Try again", "weakconnection":" "})
    elif result == "NoNewTransaction":
        return render(request, "SolanaMysteryBox/solanaMB_response.html", {"payment_response":" ",
            "text1":"No payment has been received", "link1":"Try again", "link2":"Learn More"}) 
    elif result == "NoValidTransaction":
        return render(request, "SolanaMysteryBox/solanaMB_response.html", {"payment_response":" ",
            "text1":"No valid payment has been received", "link1":"Try again", "link2":"Learn More"})
    elif result == "insufficient transaction amount":
        return render(request, "SolanaMysteryBox/solanaMB_response.html", {"payment_response":" ",
            "text1":"The payment amount is insufficient, so it has been refunded to your wallet! Please don't change the payment amount!", 
            "link1":"Try again", "link2":"Learn More"})
    elif result[1]:
        return render(request, "SolanaMysteryBox/solanaMB_response.html", {
            "payment_response":" ",
            "text1":"🎉🎉🎉Congratulations on the JACKPOT🎉🎉🎉", 
            "text2":f"🔍You have received {result[0]} Solana🔍", 
            "new":"🔮Unbox another JACKPOT🎁"
            })
    elif not result[1]:
        return render(request, "SolanaMysteryBox/solanaMB_response.html", {
            "payment_response":" ",
            "text1":"💪Small wins fuel the BIG ones💪", 
            "text2":f"🔍You have received {result[0]} Solana🔍", 
            "new":"🔮Unbox The BIG ones🎁"
            })
    