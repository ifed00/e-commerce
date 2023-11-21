# Generated by Django 4.2.7 on 2023-11-21 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='done',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='done_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='ordered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='ordered_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='ship_to',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
