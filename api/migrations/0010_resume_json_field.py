# Generated by Django 3.1 on 2020-10-09 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_alter_json_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='websiteoption',
            name='data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
