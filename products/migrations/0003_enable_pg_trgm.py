from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0002_alter_category_slug'),
    ]

    operations = [
        migrations.RunSQL(
            sql='CREATE EXTENSION IF NOT EXISTS pg_trgm;',
            reverse_sql='DROP EXTENSION IF EXISTS pg_trgm;'
        ),
    ]