from django.urls import path
from . import views
urlpatterns = [
    path('login/' , views.login_view, name='login_page'),
    path('register/' , views.register, name='register'),
    path('verify-email/<token>/' , views.verify_email_token, name='verify_email_token'),
    path('send-otp/<email>/' , views.send_otp, name='send_otp'),
    path('verify-otp/<email>/' , views.verify_otp, name='verify_otp'),
    path('login-vendor/' , views.login_vendor, name='login_vendor'),
    path('register-vendor/' , views.register_vendor, name='register_vendor'),
    path('dashboard/' , views.dashboard, name='dashboard'),
    path('add-hotel/' , views.add_hotel, name='add_hotel'),
    path('edit-hotel/<slug>/' , views.edit_hotel, name='edit_hotel'),
    path('upload-images/<slug>/' , views.upload_images, name='upload_images'),
    path('delete-image/<id>/' , views.delete_image, name='delete_image'),
    path('logout/' , views.logout_view, name='logout_view'),
    path('hotel-detail/<slug>/' , views.hotel_detail, name='hotel_detail'),
    path('book-hotel/<slug>/' , views.book_hotel, name='book_hotel'),
]