# Generated by Django 4.2.7 on 2023-12-01 15:08

import catalog.filters
import catalog.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
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
                'verbose_name_plural': 'fridge details',
            },
            bases=(catalog.filters.FilterableMixin, models.Model),
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
                'verbose_name_plural': 'phone details',
            },
            bases=(catalog.filters.FilterableMixin, models.Model),
        ),
    ]