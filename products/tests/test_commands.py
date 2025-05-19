from django.test import TestCase
from django.core.management import call_command
from products.models import Category, Product
import pytest

@pytest.mark.django_db
class PopulateProductsCommandTests(TestCase):
    def test_populate_products_command(self):
        """Test the populate_products management command."""
        # Run the command to populate products and categories
        call_command('populate_products', count=100)
        # Verify that categories are created
        self.assertGreater(Category.objects.count(), 0)
        # Verify that products are created
        self.assertGreater(Product.objects.count(), 0)