# Imports.
from django.urls import path
from TokenMysteryBox import views

# Url patterns.
urlpatterns = [
    path('', views.token_mb, name="Tokenmb"),
    path('learn', views.learn_tokenMB, name="learn-tokenMB"),
    path('PaymentView1', views.TokenMBPaymentView1, name="TokenMB-PV1"),
    path('PaymentView2', views.TokenMBPaymentView2, name="TokenMB-PV2"),
    path('PaymentView3', views.TokenMBPaymentView3, name="TokenMB-PV3"),
    path('PaymentView4', views.TokenMBPaymentView4, name="TokenMB-PV4"),
    path('PaymentView5', views.TokenMBPaymentView5, name="TokenMB-PV5"),
    path('qr/<str:box_label>/<box_price>/', views.TokenMB_GenerateQR, name='TokenMB_generate_qr'),
]
