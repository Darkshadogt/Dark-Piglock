# Generated by Django 5.0.2 on 2024-02-11 03:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_profile_reset_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardmodel',
            name='card_number',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='cardmodel',
            name='cvv',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='cardmodel',
            name='expiration_date',
            field=models.CharField(max_length=255),
        ),
    ]
