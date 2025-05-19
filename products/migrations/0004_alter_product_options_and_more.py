# D:\MiranQuest\products\migrations\0004_alter_product_options_and_more.py
import django.contrib.postgres.indexes
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0003_enable_pg_trgm'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['id'], 'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
        # التحقق مما إذا كان الفهرس موجودًا قبل إزالته
        migrations.RunSQL(
            sql="DROP INDEX IF EXISTS product_search_vector_idx;",
            reverse_sql="CREATE INDEX product_search_vector_idx ON products_product USING gin(search_vector);"
        ),
        # التحقق مما إذا كان الحقل موجودًا قبل إزالته
        migrations.RunSQL(
            sql="ALTER TABLE products_product DROP COLUMN IF EXISTS search_vector;",
            reverse_sql="ALTER TABLE products_product ADD COLUMN search_vector tsvector;"
        ),
        migrations.AddIndex(
            model_name='category',
            index=django.contrib.postgres.indexes.GinIndex(fields=['name'], name='category_name_trgm_idx', opclasses=['gin_trgm_ops']),
        ),
        migrations.AddIndex(
            model_name='product',
            index=django.contrib.postgres.indexes.GinIndex(fields=['name'], name='product_name_trgm_idx', opclasses=['gin_trgm_ops']),
        ),
        migrations.AddIndex(
            model_name='product',
            index=django.contrib.postgres.indexes.GinIndex(fields=['brand'], name='product_brand_trgm_idx', opclasses=['gin_trgm_ops']),
        ),
        migrations.AddIndex(
            model_name='product',
            index=django.contrib.postgres.indexes.GinIndex(fields=['description'], name='product_description_trgm_idx', opclasses=['gin_trgm_ops']),
        ),
    ]