"""
Django Management Command to populate the database with test product data.

This command generates and inserts a specified number of Product instances with
highly diverse product names in a mix of Arabic and English using predefined words,
Faker, and uniqueness checks. It uses bulk_create with batch processing for efficient
insertion of large datasets. Progress is displayed using tqdm. Search functionality
relies on TrigramSimilarity with pg_trgm extension.
"""

import random
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from tqdm import tqdm
from products.models import Product, Category
from django.utils.text import slugify


class Command(BaseCommand):
    """Command to populate the database with test products."""
    
    help = "Populate the database with a specified number of test products."

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            "--count",
            type=int,
            default=5000,
            help="Number of products to create (default: 1000)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=10000,
            help="Batch size for bulk_create (default: 10000)",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        count = options["count"]
        batch_size = options["batch_size"]
        fake_ar = Faker("ar_SA")  # Arabic locale
        fake_en = Faker("en_US")  # English locale
        
        self.stdout.write(self.style.SUCCESS(f"Starting to create {count} products..."))

        # Create or get categories with predefined names
        category_data = [
            {"en": "Fruits", "ar": "فواكه"},
            {"en": "Vegetables", "ar": "خضروات"},
            {"en": "Dairy", "ar": "ألبان"},
            {"en": "Grains", "ar": "حبوب"},
            {"en": "Proteins", "ar": "بروتينات"},
        ]
        categories = [
            Category.objects.get_or_create(
                name=data["en"],
                defaults={"slug": slugify(data["en"])}
            )[0]
            for data in category_data
        ]

        # Predefined words for generating diverse product names
        arabic_products = ["تفاحة", "موزة", "جبنة", "خبز", "دجاج", "برتقال", "طماطس", "حليب", "أرز", "لحم"]
        arabic_adjectives = ["طازج", "عضوي", "أحمر", "أخضر", "طبيعي", "مشوي", "ممتاز", "محلي"]
        english_products = ["Apple", "Banana", "Cheese", "Bread", "Chicken", "Orange", "Tomato", "Milk", "Rice", "Meat"]
        english_adjectives = ["Fresh", "Organic", "Red", "Green", "Natural", "Grilled", "Premium", "Local"]

        # Track used names to ensure uniqueness
        used_names = set(Product.objects.values_list('name', flat=True))

        # Generate and insert products in batches
        products = []
        total_inserted = 0
        
        with transaction.atomic():  # Ensure data consistency
            for i in tqdm(range(count), desc="Generating products"):
                # Randomly choose language for the product name
                is_arabic = random.choice([True, False])
                
                # Generate diverse and unique product name
                attempts = 0
                max_attempts = 10
                while attempts < max_attempts:
                    if is_arabic:
                        product_name = f"{random.choice(arabic_adjectives)} {random.choice(arabic_products)} {fake_ar.word().capitalize()}"
                    else:
                        product_name = f"{random.choice(english_adjectives)} {random.choice(english_products)} {fake_en.word().capitalize()}"
                    
                    if product_name not in used_names:
                        used_names.add(product_name)
                        break
                    attempts += 1
                
                # Fallback to basic name if uniqueness not achieved
                if attempts >= max_attempts:
                    product_name = f"{random.choice(arabic_adjectives)} {random.choice(arabic_products)}" if is_arabic else f"{random.choice(english_adjectives)} {random.choice(english_products)}"
                
                # Generate brand and description
                brand = fake_ar.company() if is_arabic else fake_en.company()
                description = fake_ar.sentence(nb_words=10) if is_arabic else fake_en.sentence(nb_words=10)
                
                # Create product instance
                product = Product(
                    name=product_name,
                    brand=brand,
                    description=description,
                    calories=random.randint(10, 500),
                    category=random.choice(categories),
                )
                products.append(product)
                
                # Insert batch when batch_size is reached
                if len(products) >= batch_size or i == count - 1:
                    Product.objects.bulk_create(products, batch_size=batch_size)
                    total_inserted += len(products)
                    products = []  # Clear the list for the next batch
                    self.stdout.write(
                        self.style.SUCCESS(f"Inserted {total_inserted} products so far...")
                    )

        self.stdout.write(self.style.SUCCESS(f"Successfully created {count} products!"))