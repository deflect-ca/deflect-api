# Generated by Django 3.1 on 2020-09-17 07:02

import api.models.website
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('url', models.CharField(max_length=255, unique=True)),
                ('status', models.FloatField(default=0)),
                ('ip_address', models.CharField(max_length=16)),
                ('hidden_domain', models.CharField(default=api.models.website.generate_hidden_domain, max_length=32)),
                ('banjax_auth_hash', models.CharField(default='', max_length=255)),
                ('admin_key', models.CharField(default='', max_length=255)),
                ('under_attack', models.BooleanField(default=False)),
                ('awstats_password', models.CharField(max_length=40)),
                ('ats_purge_secret', models.CharField(default=api.models.website.generate_ats_purge_secret, max_length=64)),
                ('created_at', models.DateTimeField(auto_now_add=True, editable=True)),
                ('updated_at', models.DateTimeField(auto_now=True, editable=True)),
            ],
        ),
    ]
