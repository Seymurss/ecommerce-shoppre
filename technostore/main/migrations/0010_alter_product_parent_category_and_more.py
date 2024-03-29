# Generated by Django 5.0.1 on 2024-01-28 20:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_color_product_colors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='parent_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parent_products', to='main.newcategory'),
        ),
        migrations.AlterField(
            model_name='product',
            name='sub_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sub_products', to='main.newcategory'),
        ),
        migrations.AlterField(
            model_name='product',
            name='sub_sub_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sub_sub_products', to='main.newcategory'),
        ),
    ]
