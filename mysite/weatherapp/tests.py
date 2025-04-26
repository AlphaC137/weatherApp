from django.test import TestCase
from django.contrib.auth.models import User
from .models import FavoriteCity
from django.urls import reverse

# Create your tests here.
class FavoriteCityModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create some favorite cities
        self.city1 = FavoriteCity.objects.create(
            name='London',
            user=self.test_user
        )
        self.city2 = FavoriteCity.objects.create(
            name='Paris',
            user=self.test_user
        )
    
    def test_favorite_city_creation(self):
        """Test that favorite cities are created correctly"""
        self.assertEqual(self.city1.name, 'London')
        self.assertEqual(self.city1.user, self.test_user)
        self.assertTrue(self.city1.date_added is not None)
    
    def test_favorite_city_str_representation(self):
        """Test the string representation of the FavoriteCity model"""
        self.assertEqual(str(self.city1), f"London (added by {self.test_user.username})")
    
    def test_favorite_city_ordering(self):
        """Test that cities are ordered by date_added in descending order"""
        cities = FavoriteCity.objects.all()
        self.assertEqual(cities[0], self.city2)  # Paris should be first as it was created last
        self.assertEqual(cities[1], self.city1)  # London should be second
