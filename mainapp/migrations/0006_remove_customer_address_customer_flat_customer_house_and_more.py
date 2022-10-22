# Generated by Django 4.1.2 on 2022-10-22 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0005_alter_customer_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='address',
        ),
        migrations.AddField(
            model_name='customer',
            name='flat',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='customer',
            name='house',
            field=models.CharField(default='', max_length=40),
        ),
        migrations.AddField(
            model_name='customer',
            name='korpus',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='street',
            field=models.CharField(default='', max_length=150),
        ),
        migrations.DeleteModel(
            name='Address',
        ),
    ]
