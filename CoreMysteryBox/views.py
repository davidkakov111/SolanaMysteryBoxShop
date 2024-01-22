# Import
from django.shortcuts import render

# Home view.
def index (request):
    return render(request, 'CoreMysteryBox/index.html')

# Handling 404 error view.
def handler404 (request, exception):
    return render(request, 'CoreMysteryBox/handler404.html')
