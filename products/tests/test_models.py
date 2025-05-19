import pytest
from django.test import TestCase
from django.db.utils import IntegrityError
from products.models import Category, Product
from faker import Faker

class CategoryModelTests(TestCase):
    def setUp(self):
        self.faker = Faker()

    def test_category_creation(self):
        """Test that a category can be created with valid data."""
        category = Category.objects.create(
            name=self.faker.word(),
            description=self.faker.text(),
            slug=self.faker.slug()
        )
        self.assertTrue(category.id)
        self.assertEqual(category.name, category.name)

    def test_category_string_representation(self):
        """Test the string representation of a category."""
        category = Category.objects.create(name=self.faker.word())
        self.assertEqual(str(category), category.name)

    def test_category_unique_name(self):
        """Test that category names must be unique."""
        name = self.faker.word()
        Category.objects.create(name=name)
        with self.assertRaises(IntegrityError):
            Category.objects.create(name=name)


@pytest.mark.django_db
class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fruits")

    def test_product_creation(self):
        """Test creating a product with all fields."""
        product = Product.objects.create(
            name="Apple",
            brand="Organic",
            category=self.category,
            description="Fresh red apple",
            calories=52,
            protein=0.3,
            carbs=14.0,
            fats=0.2
        )
        self.assertEqual(product.name, "Apple")
        self.assertEqual(product.brand, "Organic")
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.calories, 52)
        self.assertTrue(product.created_at)
        self.assertTrue(product.updated_at)

    def test_product_string_representation(self):
        """Test the string representation of a product."""
        product = Product.objects.create(
            name="Apple", brand="Organic", category=self.category
        )
        self.assertEqual(str(product), "Apple (Organic)")
