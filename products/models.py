"""
Models for the Products app in the Miran Search project.

This module defines the Category and Product models with trigram indexes
for efficient search and composite indexes for optimized filtering.
"""

from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.utils.text import slugify


class Category(models.Model):
    """
    Represents a product category (e.g., Fruits, Proteins) for organizing products.

    Attributes:
        name (CharField): The name of the category (e.g., "Fruits").
        description (TextField): Optional description of the category.
        slug (SlugField): URL-friendly identifier for the category.
        created_at (DateTimeField): Timestamp when the category was created.
        updated_at (DateTimeField): Timestamp when the category was last updated.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=120, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]
        indexes = [
            GinIndex(fields=["name"], name="category_name_trgm_idx", opclasses=["gin_trgm_ops"]),
        ]

    def save(self, *args, **kwargs):
        """
        Automatically generate a unique slug based on the category name.
        """
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Represents a product (e.g., food item, supplement) with nutritional information
    and full-text search capabilities.

    Attributes:
        name (CharField): The name of the product (e.g., "Apple").
        brand (CharField): The brand of the product (e.g., "Organic").
        category (ForeignKey): The category to which the product belongs.
        description (TextField): Detailed description of the product.
        calories (IntegerField): Calories per serving.
        protein (FloatField): Protein content in grams.
        carbs (FloatField): Carbohydrates content in grams.
        fats (FloatField): Fats content in grams.
        created_at (DateTimeField): Timestamp when the product was created.
        updated_at (DateTimeField): Timestamp when the product was last updated.
    """
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    description = models.TextField(blank=True)
    calories = models.IntegerField(default=0)
    protein = models.FloatField(default=0.0)
    carbs = models.FloatField(default=0.0)
    fats = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["id"]
        indexes = [
            GinIndex(
                fields=["name", "brand"],
                name="product_name_brand_trgm_idx",
                opclasses=["gin_trgm_ops", "gin_trgm_ops"]
            ),
            models.Index(
                fields=["category", "calories"],
                name="product_category_calories_idx"
            ),
            GinIndex(fields=["name"], name="product_name_trgm_idx", opclasses=["gin_trgm_ops"]),
            GinIndex(fields=["brand"], name="product_brand_trgm_idx", opclasses=["gin_trgm_ops"]),
            GinIndex(fields=["description"], name="product_description_trgm_idx", opclasses=["gin_trgm_ops"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.brand})"