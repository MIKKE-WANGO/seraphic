# Generated by Django 4.0.4 on 2022-11-06 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotation', '0012_rename_category_product_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='phone',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
