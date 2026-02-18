from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import HotelUser, HotelVendor, Hotel, Amenities

class VendorFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register_vendor')
        self.login_url = reverse('login_vendor')
        self.add_hotel_url = reverse('add_hotel')
        self.dashboard_url = reverse('dashboard')
        
        # Create a user for login testing
        self.vendor_user = User.objects.create_user(username='1234567890', email='vendor@test.com', password='password123')
        self.vendor = HotelVendor.objects.create(
            user=self.vendor_user,
            phone_number='1234567890',
            business_name='Test Hotel Inc',
            is_verified=True
        )

    def test_vendor_registration(self):
        """Test that a vendor can register."""
        response = self.client.post(self.register_url, {
            'first_name': 'New',
            'last_name': 'Vendor',
            'business_name': 'New Biz',
            'email': 'newvendor@test.com',
            'phone_number': '0987654321',
            'password': 'password123'
        })
        # Should redirect to register page with success message
        self.assertEqual(response.status_code, 302)
        self.assertTrue(HotelVendor.objects.filter(user__email='newvendor@test.com').exists())

    def test_vendor_login(self):
        """Test that a verified vendor can login."""
        # Test that valid credentials redirect to dashboard
        response = self.client.post(self.login_url, {
            'email': 'vendor@test.com',
            'password': 'password123'
        }, follow=True)
        
        # If this fails, it might be due to test environment auth issues
        # We'll print the response content to see any error messages
        if response.redirect_chain[-1][0] != self.dashboard_url:
             print(f"Redirect failed. Final URL: {response.redirect_chain[-1][0]}")
             # Check for messages
             messages = list(response.context['messages'])
             for m in messages:
                 print(f"Message: {m}")

        self.assertRedirects(response, self.dashboard_url)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_add_hotel(self):
        """Test adding a hotel."""
        self.client.login(username='1234567890', password='password123')
        
        # Create some amenities
        a1 = Amenities.objects.create(name='Wifi')
        a2 = Amenities.objects.create(name='Pool')
        
        response = self.client.post(self.add_hotel_url, {
            'hotel_name': 'My Grand Hotel',
            'hotel_description': 'A very nice place',
            'hotel_price': '100',
            'hotel_offer_price': '80',
            'hotel_location': 'New York',
            'ameneties': [a1.id, a2.id]
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Hotel.objects.filter(hotel_name='My Grand Hotel').exists())
        hotel = Hotel.objects.get(hotel_name='My Grand Hotel')
        self.assertEqual(hotel.amenities.count(), 2)


class UserFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login_page')
        
        # Create a hotel to book
        user = User.objects.create_user(username='vendor', email='v@t.com', password='password')
        vendor = HotelVendor.objects.create(user=user, phone_number='111', is_verified=True)
        self.hotel = Hotel.objects.create(
            hotel_name='Bookable Hotel',
            hotel_description='Desc',
            hotel_price=100,
            hotel_offer_price=90,
            hotel_location='City',
            hotel_slug='bookable-hotel',
            hotel_owner=vendor
        )
        
        # Create verified user
        self.user_user = User.objects.create_user(username='5555555555', email='user@test.com', password='password')
        self.hotel_user = HotelUser.objects.create(
            user=self.user_user,
            phone_number='5555555555',
            is_verified=True
        )

    def test_user_booking(self):
        """Test booking a hotel."""
        self.client.login(username='5555555555', password='password')
        
        book_url = reverse('book_hotel', args=[self.hotel.hotel_slug])
        response = self.client.post(book_url, {
            'start_date': '2024-01-01',
            'end_date': '2024-01-05' # 4 nights
        })
        
        self.assertEqual(response.status_code, 302)
        # Check booking exists
        from .models import HotelBooking
        self.assertTrue(HotelBooking.objects.filter(hotel=self.hotel).exists())
        booking = HotelBooking.objects.first()
        self.assertEqual(booking.price, 360.0) # 90 * 4