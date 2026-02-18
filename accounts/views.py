from django.shortcuts import render, redirect
from .models import HotelUser , HotelVendor, Hotel, Amenities, HotelImages
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from .utils import generateRandomToken, sendEmailToken , sendOTPtoEmail
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
import random
from django.contrib.auth.decorators import login_required
from .utils import generateSlug
from django.http import HttpResponseRedirect
from datetime import datetime
from .models import HotelBooking

# Create your views here.
def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = User.objects.filter(email = email).first()
        if user_obj is None:
            messages.warning(request, "No Account Found.")
            return redirect('/account/login/')

        if not hasattr(user_obj, 'hoteluser'):
             messages.warning(request, "Not a valid hotel user.")
             return redirect('/account/login/')
        
        hotel_user = user_obj.hoteluser

        if not hotel_user.is_verified:
            messages.warning(request, "Account not verified")
            return redirect('/account/login/')

        user = authenticate(username = user_obj.username , password=password)

        if user:
            messages.success(request, "Login Success")
            login(request , user)
            return redirect('/') # Redirect to home

        messages.warning(request, "Invalid credentials")
        return redirect('/account/login/')
    return render(request, 'login.html')


def register(request):
    if request.method == "POST":

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        if User.objects.filter(email = email).exists():
            messages.warning(request, "Account exists with this Email.")
            return redirect('/account/register/')
            
        if HotelUser.objects.filter(phone_number=phone_number).exists():
             messages.warning(request, "Account exists with this Phone Number.")
             return redirect('/account/register/')

        user = User.objects.create(
            first_name = first_name,
            last_name = last_name,
            email = email,
            username = phone_number, # Using phone as username
        )
        user.set_password(password)
        user.save()

        hotel_user = HotelUser.objects.create(
            user = user,
            phone_number = phone_number,
            email_token = generateRandomToken()
        )
        # remove save here as create saves it
        
        sendEmailToken(email , hotel_user.email_token)

        messages.success(request, "An email Sent to your Email")
        return redirect('/account/register/')

    return render(request, 'register.html')


def verify_email_token(request, token):
    try:
        hotel_user = HotelUser.objects.get(email_token = token)
        hotel_user.is_verified = True
        hotel_user.save()
        messages.success(request, "Email verified")
        return redirect('/account/login/')
    except Exception as e:
        return HttpResponse("Invalid Token")
    



def send_otp(request, email):
    hotel_user = HotelUser.objects.filter(
            user__email = email)
    if not hotel_user.exists():
            messages.warning(request, "No Account Found.")
            return redirect('/account/login/')

    otp =  random.randint(1000 , 9999)
    hotel_user.update(otp =otp)

    sendOTPtoEmail(email , otp)

    return redirect(f'/account/verify-otp/{email}/')

def verify_otp(request , email):
    if request.method == "POST":
        otp  = request.POST.get('otp')
        hotel_user = HotelUser.objects.filter(user__email = email).first()
        
        if not hotel_user:
             messages.warning(request, "No Account Found")
             return redirect(f'/account/verify-otp/{email}/')

        if str(otp) == str(hotel_user.otp):
            messages.success(request, "Login Success")
            login(request , hotel_user.user)
            return redirect('/account/login/')
        
        messages.warning(request, "Wrong OTP")
        return redirect(f'/account/verify-otp/{email}/')
    
    return render(request , 'verify_otp.html')



# Create your views here.
def login_vendor(request):    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = User.objects.filter(email = email).first()
        if user_obj is None:
            messages.warning(request, "No Account Found.")
            return redirect('/account/login-vendor/')

        if not hasattr(user_obj, 'hotelvendor'):
             messages.warning(request, "Not a valid vendor account.")
             return redirect('/account/login-vendor/')
             
        hotel_vendor = user_obj.hotelvendor

        if not hotel_vendor.is_verified:
            messages.warning(request, "Account not verified")
            return redirect('/account/login-vendor/')

        user = authenticate(username = user_obj.username , password=password)

        if user:
            login(request , user)
            return redirect('/account/dashboard/')

        messages.warning(request, "Invalid credentials")
        return redirect('/account/login-vendor/')
    return render(request, 'vendor/login_vendor.html')


def register_vendor(request):
    if request.method == "POST":

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        business_name = request.POST.get('business_name')

        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        if User.objects.filter(email = email).exists():
            messages.warning(request, "Account exists with this Email.")
            return redirect('/account/register-vendor/')
            
        if HotelVendor.objects.filter(phone_number=phone_number).exists():
             messages.warning(request, "Account exists with this Phone Number.")
             return redirect('/account/register-vendor/')

        user = User.objects.create(
            first_name = first_name,
            last_name = last_name,
            email = email,
            username = phone_number,
        )
        user.set_password(password)
        user.save()

        hotel_vendor = HotelVendor.objects.create(
            user = user,
            phone_number = phone_number,
            business_name = business_name,
            email_token = generateRandomToken()
        )
        
        sendEmailToken(email , hotel_vendor.email_token)

        messages.success(request, "An email Sent to your Email")
        return redirect('/account/register-vendor/')


    return render(request, 'vendor/register_vendor.html')


@login_required(login_url='login_vendor')
def dashboard(request):
    try:
        hotel_vendor = HotelVendor.objects.get(user=request.user)
        hotels = Hotel.objects.filter(hotel_owner=hotel_vendor)
    except HotelVendor.DoesNotExist:
        hotels = []
    context = {'hotels' : hotels}
    return render(request, 'vendor/vendor_dashboard.html', context)


@login_required(login_url='login_vendor')
def add_hotel(request):
    if request.method == "POST":
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        ameneties= request.POST.getlist('ameneties')
        hotel_price= request.POST.get('hotel_price')
        hotel_offer_price= request.POST.get('hotel_offer_price')
        hotel_location= request.POST.get('hotel_location')
        hotel_slug = generateSlug(hotel_name)

        hotel_vendor = HotelVendor.objects.get(user = request.user)

        hotel_obj = Hotel.objects.create(
            hotel_name = hotel_name,
            hotel_description = hotel_description,
            hotel_price = hotel_price,
            hotel_offer_price = hotel_offer_price,
            hotel_location = hotel_location,
            hotel_slug = hotel_slug,
            hotel_owner = hotel_vendor
        )

        for ameneti in ameneties:
            ameneti = Amenities.objects.get(id = ameneti)
            hotel_obj.amenities.add(ameneti)
            hotel_obj.save()


        messages.success(request, "Hotel Created")
        return redirect('/account/add-hotel/')


    ameneties = Amenities.objects.all()
        
    return render(request, 'vendor/add_hotel.html', context = {'ameneties' : ameneties})
    


@login_required(login_url='login_vendor')
def upload_images(request, slug):
    hotel_obj = Hotel.objects.get(hotel_slug = slug)
    if request.user != hotel_obj.hotel_owner.user:
        return HttpResponse("You are not authorized")
    if request.method == "POST":
        image = request.FILES['image']
        print(image)
        HotelImages.objects.create(
        hotel = hotel_obj,
        image = image
        )
        return HttpResponseRedirect(request.path_info)
     
    return render(request, 'vendor/upload_images.html', context = {'images' : hotel_obj.hotel_images.all()})

@login_required(login_url='login_vendor')
def delete_image(request, id):

    hotel_image = HotelImages.objects.get(id = id)
    hotel_image.delete()
    messages.success(request, "Hotel Image deleted")
    return redirect('/account/dashboard/')


@login_required(login_url='login_vendor')
def edit_hotel(request, slug):
    hotel_obj = Hotel.objects.get(hotel_slug = slug)
    if request.user != hotel_obj.hotel_owner.user:
        return HttpResponse("You are not authorized")

    if request.method == "POST":
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        hotel_price= request.POST.get('hotel_price')
        hotel_offer_price= request.POST.get('hotel_offer_price')
        hotel_location= request.POST.get('hotel_location')
        hotel_obj.hotel_name  = hotel_name
        hotel_obj.hotel_description  = hotel_description
        hotel_obj.hotel_price  = hotel_price
        hotel_obj.hotel_offer_price  = hotel_offer_price
        hotel_obj.hotel_location  = hotel_location
        hotel_obj.save()
        messages.success(request, "Hotel Details Updated")

        return HttpResponseRedirect(request.path_info)
     
    ameneties = Amenities.objects.all()
    return render(request, 'vendor/edit_hotel.html', context = {'hotel' : hotel_obj, 'ameneties' : ameneties})


def logout_view(request):
    logout(request)
    return redirect('/account/login/')
def hotel_detail(request, slug):
    try:
        hotel_obj = Hotel.objects.get(hotel_slug = slug)
    except Exception as e:
        return redirect('/')
        
    return render(request, 'hotel_detail.html', context = {'hotel' : hotel_obj})


@login_required(login_url='login_page')
def book_hotel(request, slug):
    hotel_obj = Hotel.objects.get(hotel_slug = slug)
    
    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        if not start_date or not end_date:
            messages.warning(request, "Please select start and end dates")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
        # Basic validation
        from datetime import datetime
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start >= end:
             messages.warning(request, "Check-out date must be after check-in date")
             return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
             
        # simplistic price calculation
        days = (end - start).days
        price = hotel_obj.hotel_offer_price * days
        
        # User is guaranteed to be logged in due to decorator, but model expects HotelUser instance for booking_user
        # The User model is linked to HotelUser one-to-one.
        try:
             hotel_user = HotelUser.objects.get(user=request.user)
        except HotelUser.DoesNotExist:
             messages.warning(request, "You must be a registered customer to book.")
             return redirect('/')
             
        
        HotelBooking.objects.create(
            hotel = hotel_obj,
            booking_user = hotel_user, # Assuming logged in user has a HotelUser profile
            booking_start_date = start_date,
            booking_end_date = end_date,
            price = price
        )
        
        messages.success(request, "Booking Successful!")
        return redirect('/')
        
    return redirect('/')
