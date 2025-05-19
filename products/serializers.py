from rest_framework import serializers
from .models import Product, Category
from django.utils.text import slugify


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.

    Converts Category instances into JSON, including essential fields like name and slug.
    Designed to be used standalone or nested within other serializers (e.g., ProductSerializer).

    Fields:
        id (int): Unique identifier for the category.
        name (str): Name of the category (e.g., "Fruits").
        slug (str): URL-friendly identifier for the category.
    """
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]
        read_only_fields = ["id", "slug"]


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.

    Allows creating/updating products with a category specified by name (string).
    If the category doesn't exist, it will be created automatically.
    """
    category = CategorySerializer(read_only=True)
    category = serializers.CharField(write_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "brand",
            "category",
            "description",
            "calories",
            "protein",
            "carbs",
            "fats",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_category(self, value):
        """
        Validate the category field and return the corresponding Category instance.
        If the category doesn't exist, create a new one.
        """
        if not value:
            raise serializers.ValidationError("Category name cannot be empty.")
        category, created = Category.objects.get_or_create(
            slug=slugify(value),
            defaults={"name": value, "description": f"{value} category"}
        )
        return category

    def create(self, validated_data):
        """
        Create a new product with the validated data.
        """
        category = validated_data.pop("category")
        validated_data["category"] = category
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing product with the validated data.
        """
        category = validated_data.pop("category", None)
        if category:
            instance.category = category
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ProductSearchSerializer(ProductSerializer):
    """
    Specialized serializer for product search results.
    Currently identical to ProductSerializer but separated for future flexibility.
    """
    rank = serializers.FloatField(read_only=True)
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ["rank"]
