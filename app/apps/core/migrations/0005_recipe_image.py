# Generated by Django 3.2.9 on 2021-11-24 18:30

import apps.core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_recipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='image',
            field=models.ImageField(null=True, upload_to=apps.core.models.recipe_image_file_path),
        ),
    ]