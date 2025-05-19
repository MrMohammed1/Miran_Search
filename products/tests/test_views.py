from django.test import TestCase
from rest_framework.test import APIClient
from django.core.cache import cache
from products.models import Category, Product
from products.views import normalize_arabic
from django.contrib.auth.models import User
import pytest

@pytest.mark.django_db
class ProductViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name="Fruits", slug="fruits")
        self.product = Product.objects.create(
            name="Apple", brand="Organic", category=self.category, calories=52
        )
        # Obtain JWT token
        response = self.client.post(
            '/api/token/',
            {'username': 'testuser', 'password': 'testpass'},
            format='json'
        )
        self.access_token = response.data['access']

    def test_list_products(self):
        """Test listing all products with caching."""
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("results" in response.data)
        self.assertTrue(len(response.data["results"]) > 0)
        cached_data = cache.get("products:all:page:1")
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data, response.data)

    def test_retrieve_product(self):
        """Test retrieving a single product with caching."""
        response = self.client.get(f"/api/products/{self.product.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Apple")
        cached_data = cache.get(f"products:{self.product.id}")
        self.assertIsNotNone(cached_data)

    def test_create_product(self):
        """Test creating a product with JWT authentication and cache invalidation."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {
            "name": "Banana",
            "brand": "Organic",
            "category": "Fruits",
            "calories": 89
        }
        response = self.client.post("/api/products/", data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "Banana")
        self.assertIsNone(cache.get("products:all"))

    def test_search_products(self):
        """Test searching products by name."""
        response = self.client.get("/api/products/search/?q=Apple")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("results" in response.data)
        self.assertTrue(len(response.data["results"]) > 0)

    def test_search_with_filters(self):
        """Test searching with category and calories filters."""
        response = self.client.get(
            "/api/products/search/?q=Apple&category=Fruits&calories_min=50&calories_max=100"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Apple")

    def test_search_arabic(self):
        """Test searching with Arabic query and normalization."""
        product = Product.objects.create(
            name="تفاح", brand="Organic", category=self.category, calories=52
        )
        response = self.client.get("/api/products/search/?q=تفإح")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "تفاح")

    def test_search_empty_query(self):
        """Test search with empty query returns empty list."""
        response = self.client.get("/api/products/search/?q=")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 0)

    def test_search_invalid_calories(self):
        """Test search with invalid calories_min/max logs warning but continues."""
        response = self.client.get("/api/products/search/?q=Apple&calories_min=invalid")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

@pytest.mark.django_db
class CategoryViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name="Fruits", slug="fruits")
        # Obtain JWT token
        response = self.client.post(
            '/api/token/',
            {'username': 'testuser', 'password': 'testpass'},
            format='json'
        )
        self.access_token = response.data['access']

    def test_list_categories(self):
        """Test listing all categories."""
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Fruits")

    def test_create_category(self):
        """Test creating a category with JWT authentication."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {"name": "Vegetables"}
        response = self.client.post("/api/categories/", data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "Vegetables")