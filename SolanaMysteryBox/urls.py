# Imports.
from django.urls import path
from SolanaMysteryBox import views

# Url patterns.
urlpatterns = [
    path('', views.solana_mb, name="Solanamb"),
    path('qr/<str:box_label>/<box_price>/', views.SolanaMB_GenerateQR, name='SolanaMB_generate_qr'),
    path('learn', views.learn_solanaMB, name="learn-solanaMB"),
    path('PaymentView', views.SolanaMBPaymentView, name="SolanaMB-PV"),
    ]
