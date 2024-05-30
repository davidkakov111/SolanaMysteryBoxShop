# Imports
from solana_pay import PaymentRequest
from solana.publickey import PublicKey
import qrcode, base64
from io import BytesIO

# QR code transaction builder.
def QRPay(recipent, amount, label="MysteryBox",
        qr_fill_color="black", qr_bg_color="white"):
    # PaymentRequest obj. to url
    payment_request = PaymentRequest(
        recipient=PublicKey(recipent),
        amount=amount,
        label=label
    ).to_url()
    # Creating QR Code.
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(payment_request)
    qr.make(fit=True)
    img = qr.make_image(fill_color=qr_fill_color, back_color=qr_bg_color)
    # Creating data URL from the QR code.
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_code_data_url = base64.b64encode(buffered.getvalue()).decode()
    # Return the data URL.
    return qr_code_data_url
