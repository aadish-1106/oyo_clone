from django.shortcuts import render

# Create your views here.

from accounts.models import Hotel

def index(request):
    hotels = Hotel.objects.all()
    return render(request, 'index.html', context = {'hotels' : hotels})

def login_page(request):
    return render(request, 'login.html')

def register_page(request):
    return render(request, 'register.html')