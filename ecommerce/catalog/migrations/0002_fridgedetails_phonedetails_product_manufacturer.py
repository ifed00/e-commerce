# Generated by Django 4.2.7 on 2023-11-09 15:13

import catalog.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FridgeDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('volume_liters', models.PositiveIntegerField()),
                ('has_freezer', models.BooleanField()),
                ('color', models.CharField(default='White', max_length=32)),
                ('EU_energy_label', models.CharField(choices=[('A+++', 'A+++'), ('A++', 'A++'), ('A+', 'A+'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('G', 'G')], max_length=8)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PhoneDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('memory_KB', models.PositiveIntegerField()),
                ('display_resolution', models.CharField(max_length=16, validators=[catalog.validators.validate_resolution])),
                ('camera_resolution', models.CharField(max_length=16, validators=[catalog.validators.validate_resolution])),
                ('color', models.CharField(max_length=32)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='product',
            name='manufacturer',
            field=models.CharField(default='BOSH', max_length=255),
            preserve_default=False,
        ),
    ]
