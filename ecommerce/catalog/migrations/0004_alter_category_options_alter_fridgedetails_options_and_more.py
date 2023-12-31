# Generated by Django 4.2.7 on 2023-11-11 08:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'categories'},
        ),
        migrations.AlterModelOptions(
            name='fridgedetails',
            options={'verbose_name_plural': 'fridge details'},
        ),
        migrations.AlterModelOptions(
            name='phonedetails',
            options={'verbose_name_plural': 'phone details'},
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.category'),
        ),
    ]
