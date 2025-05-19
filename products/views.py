import logging
import unicodedata
from django.db.models import Q, Value, BooleanField, Case, When
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework import viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.cache import cache
from django_redis import get_redis_connection
from .models import Product, Category
from .serializers import ProductSerializer, ProductSearchSerializer, CategorySerializer

# Logger setup
logger = logging.getLogger(__name__)


def normalize_arabic(text):
    """
    Normalize Arabic characters for unified search matching 
    (e.g., replace 'أ', 'إ', 'آ' with 'ا', and 'ة' with 'ه').
    """
    text = unicodedata.normalize('NFKD', text)
    replacements = {'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ة': 'ه'}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


class StandardResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class for consistent results pagination.
    """
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products including search, caching, and cache invalidation.
    """
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        """
        Use a dedicated serializer when performing a search.
        """
        if self.action == 'search':
            return ProductSearchSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        """
        Allow unrestricted access to listing, retrieving, and searching products.
        Restrict other actions.
        """
        if self.action in ['list', 'retrieve', 'search']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        """
        List products with caching support.
        """
        page_number = request.query_params.get('page', '1')
        cache_key = f"products:all:page:{page_number}"
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.debug(f"[CACHE HIT] {cache_key}")
            return Response(cached_response)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=600)
        return response

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single product with caching support.
        """
        product_id = kwargs.get('pk')
        cache_key = f"products:{product_id}"
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.debug(f"[CACHE HIT] {cache_key}")
            return Response(cached_response)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=600)
        return response

    def perform_create(self, serializer):
        """
        Create a new product and invalidate relevant caches.
        """
        product = serializer.save()
        self.invalidate_product_cache(product.id)

    def perform_update(self, serializer):
        """
        Update a product and invalidate relevant caches.
        """
        product = serializer.save()
        self.invalidate_product_cache(product.id)

    def perform_destroy(self, instance):
        """
        Delete a product and invalidate relevant caches.
        """
        product_id = instance.id
        instance.delete()
        self.invalidate_product_cache(product_id)

    def invalidate_product_cache(self, product_id):
        """
        Clear product detail and product list caches.
        """
        cache.delete_pattern("products:all:*")
        cache.delete(f"products:{product_id}")
        self.invalidate_all_search_cache()

    def invalidate_all_search_cache(self):
        """
        Clear all search-related keys stored in Redis.
        """
        redis = get_redis_connection("default")
        keys = redis.smembers("search_keys")
        if keys:
            redis.delete(*keys, "search_keys")
            logger.debug("[CACHE CLEARED] search:*")

    def _search_queryset(self, query, category, calories_min, calories_max):
        """
        Search logic based on trigram similarity, category, and calorie filters.
        """
        query = normalize_arabic(query)
        if category:
            category = normalize_arabic(category)

        queryset = Product.objects.select_related('category')

        if category:
            queryset = queryset.filter(category__name__icontains=category)

        if calories_min:
            try:
                queryset = queryset.filter(calories__gte=float(calories_min))
            except ValueError:
                logger.warning(f"Invalid calories_min value: {calories_min}")

        if calories_max:
            try:
                queryset = queryset.filter(calories__lte=float(calories_max))
            except ValueError:
                logger.warning(f"Invalid calories_max value: {calories_max}")

        if len(query) <= 2:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(brand__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            ).annotate(
                is_exact_name_match=Case(
                    When(name__icontains=query, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            ).order_by('-is_exact_name_match', 'name')
        else:
            queryset = queryset.annotate(
                rank=(
                    TrigramSimilarity('name', query) * 2.0 +
                    TrigramSimilarity('brand', query) * 1.0 +
                    TrigramSimilarity('description', query) * 0.5 +
                    TrigramSimilarity('category__name', query) * 0.8
                ),
                is_exact_name_match=Case(
                    When(name__icontains=query, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            ).filter(rank__gt=0.2).order_by('-is_exact_name_match', '-rank', 'name')

        return queryset

    @action(detail=False, methods=['get'], url_path='search')
    @permission_classes([AllowAny])
    def search(self, request):
        """
        Search endpoint for querying products with TrigramSimilarity and filters.
        """
        query = request.query_params.get('q', '').strip()
        category = request.query_params.get('category')
        calories_min = request.query_params.get('calories_min')
        calories_max = request.query_params.get('calories_max')

        if not query:
            return Response({
                "count": 0,
                "next": None,
                "previous": None,
                "results": []
            })

        queryset = self._search_queryset(query, category, calories_min, calories_max)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        """
        Allow unrestricted access to category listing and details.
        """
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return super().get_permissions()
