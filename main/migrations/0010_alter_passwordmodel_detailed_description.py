# Generated by Django 4.2.7 on 2024-01-08 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_cardmodel_card_type_alter_cardmodel_expiration_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordmodel',
            name='detailed_description',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
    ]