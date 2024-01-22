# Imports.
from django.urls import path
from NFTMysteryBox import views

# Url patterns.
urlpatterns = [
    path('', views.NFT_mb, name="NFTmb"),
    path('learn', views.learn_NFTMB, name="learn-NFTMB"),
    path('PaymentView1', views.NFTMBPaymentView1, name="NFTMB-PV1"),
    path('PaymentView2', views.NFTMBPaymentView2, name="NFTMB-PV2"),
    path('PaymentView3', views.NFTMBPaymentView3, name="NFTMB-PV3"),
    path('qr/<str:box_label>/<box_price>/', views.NFTMB_GenerateQR, name='NFTMB_generate_qr'),
    ]
