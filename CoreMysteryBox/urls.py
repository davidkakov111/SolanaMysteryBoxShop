"""
URL configuration for CoreMysteryBox project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# Imports.
from django.conf.urls.static import static
from django.urls import include, path
from CoreMysteryBox import views
from django.conf import settings
from django.contrib import admin

# Url patterns.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="home"),
    path('TokenMysteryBoxes/', include('TokenMysteryBox.urls')),
    path('SolanaMysteryBoxes/', include('SolanaMysteryBox.urls')),
    path('NFTMysteryBoxes/', include('NFTMysteryBox.urls')),
]
# For handling 404 error
handler404 = 'CoreMysteryBox.views.handler404'
# For Vercel
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_ROOT, document_root=settings.STATIC_ROOT)
