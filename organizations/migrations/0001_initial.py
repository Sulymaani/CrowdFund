# Generated by Django 5.1.7 on 2025-06-16 17:28

import core.validators
import organizations.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('mission', models.TextField(blank=True, null=True)),
                ('contact_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('logo', models.ImageField(blank=True, help_text='Organization logo (max 800x800px, 2MB, formats: JPEG, PNG, SVG)', null=True, upload_to=organizations.models.org_logo_path, validators=[core.validators.FileSizeValidator(2), core.validators.ImageDimensionsValidator(800, 800), core.validators.ImageFormatValidator(['JPEG', 'PNG', 'SVG'])])),
                ('banner', models.ImageField(blank=True, help_text='Organization banner (max 1920x480px, 3MB, formats: JPEG, PNG)', null=True, upload_to=organizations.models.org_banner_path, validators=[core.validators.FileSizeValidator(3), core.validators.ImageDimensionsValidator(1920, 480), core.validators.ImageFormatValidator(['JPEG', 'PNG'])])),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Organisation',
                'verbose_name_plural': 'Organisations',
                'ordering': ['name'],
            },
        ),
    ]
