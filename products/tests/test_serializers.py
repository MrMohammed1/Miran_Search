from django.test import TestCase
from rest_framework.exceptions import ValidationError
from products.models import Category, Product
from products.serializers import CategorySerializer, ProductSerializer, ProductSearchSerializer
import pytest

@pytest.mark.django_db
class CategorySerializerTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fruits", slug="fruits")

    def test_serialize_category(self):
        """Test serializing a category."""
        serializer = CategorySerializer(self.category)
        expected_data = {
            "id": self.category.id,
            "name": "Fruits",
            "slug": "fruits"
        }
        self.assertEqual(serializer.data, expected_data)

    def test_deserialize_category(self):
        """Test deserializing a category."""
        data = {"name": "Vegetables", "slug": "vegetables"}
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        category = serializer.save()
        self.assertEqual(category.name, "Vegetables")

@pytest.mark.django_db
class ProductSerializerTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fruits", slug="fruits")
        self.product = Product.objects.create(
            name="Apple", brand="Organic", category=self.category, calories=52
        )

    def test_serialize_product(self):
        """Test serializing a product."""
        serializer = ProductSerializer(self.product)
        expected_data = {
            "id": self.product.id,
            "name": "Apple",
            "brand": "Organic",
            "description": "",
            "calories": 52,
            "protein": 0.0,
            "carbs": 0.0,
            "fats": 0.0,
            "created_at": self.product.created_at.isoformat(),
            "updated_at": self.product.updated_at.isoformat()
        }
        self.assertEqual(serializer.data["name"], expected_data["name"])
        self.assertEqual(serializer.data["brand"], expected_data["brand"])
        self.assertEqual(serializer.data["calories"], expected_data["calories"])

    def test_deserialize_product_create(self):
        """Test creating a product with a new category."""
        data = {
            "name": "Banana",
            "brand": "Organic",
            "category": "Fruits",
            "calories": 89
        }
        serializer = ProductSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        product = serializer.save()
        self.assertEqual(product.name, "Banana")
        self.assertEqual(product.category.name, "Fruits")

    def test_deserialize_product_update(self):
        """Test updating a product with an existing category."""
        data = {
            "name": "Green Apple",
            "brand": "Organic",
            "category": "Fruits",
            "calories": 48
        }
        serializer = ProductSerializer(self.product, data=data)
        self.assertTrue(serializer.is_valid())
        updated_product = serializer.save()
        self.assertEqual(updated_product.name, "Green Apple")
        self.assertEqual(updated_product.calories, 48)

    def test_invalid_category(self):
        """Test validation error for empty category."""
        data = {
            "name": "Banana",
            "brand": "Organic",
            "category": "",
            "calories": 89
        }
        serializer = ProductSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

@pytest.mark.django_db
class ProductSearchSerializerTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fruits", slug="fruits")
        self.product = Product.objects.create(
            name="Apple", brand="Organic", category=self.category, calories=52
        )

    def test_serialize_search_result(self):
        """Test serializing a product with rank for search results."""
        serializer = ProductSearchSerializer(self.product, context={"rank": 0.95})
        self.assertEqual(serializer.data["name"], "Apple")
