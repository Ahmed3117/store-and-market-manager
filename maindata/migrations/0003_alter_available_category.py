# Generated by Django 4.1.3 on 2023-08-29 15:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('maindata', '0002_available_category_alter_product_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='available',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='maindata.category', verbose_name=' التصنيف'),
        ),
    ]
