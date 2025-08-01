# Generated by Django 5.1.7 on 2025-06-16 17:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organizations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('description', models.TextField()),
                ('funding_goal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('category', models.CharField(choices=[('education', 'Education'), ('healthcare', 'Healthcare'), ('environment', 'Environment'), ('poverty', 'Poverty Relief'), ('arts', 'Arts & Culture'), ('disaster', 'Disaster Relief'), ('community', 'Community Development'), ('animals', 'Animal Welfare'), ('technology', 'Technology'), ('other', 'Other')], max_length=50)),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='campaign_covers/')),
                ('status', models.CharField(choices=[('active', 'Active'), ('pending', 'Pending'), ('closed', 'Closed'), ('rejected', 'Rejected'), ('draft', 'Draft')], default='draft', max_length=20)),
                ('rejection_reason', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mod_campaigns_created', to=settings.AUTH_USER_MODEL)),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaigns', to='organizations.organisation')),
            ],
            options={
                'verbose_name': 'Campaign',
                'verbose_name_plural': 'Campaigns',
                'ordering': ['-created_at'],
                'permissions': [('review_campaign', 'Can review campaigns'), ('close_campaign', 'Can close campaigns'), ('reactivate_campaign', 'Can reactivate campaigns')],
            },
        ),
    ]
