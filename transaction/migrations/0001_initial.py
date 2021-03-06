# Generated by Django 2.1.7 on 2020-07-28 11:34

import datetime
from django.db import migrations, models
import transaction.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isActive', models.BooleanField(default=True)),
                ('transno', models.CharField(default=transaction.models.creatransno, max_length=50, unique=True)),
                ('quantity', models.FloatField()),
                ('nbids', models.IntegerField(default=0)),
                ('description', models.TextField()),
                ('deadline', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('SD', 'Delivery for Storage'), ('TD1', 'Delivery for Sale from Farmer'), ('TD2', 'Delivery for Sale from Warehouse')], max_length=3)),
                ('locked', models.BooleanField(default=False, null=True)),
                ('cost', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlaceBid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Produce',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.CharField(max_length=50)),
                ('quantity', models.FloatField()),
                ('price', models.FloatField()),
                ('date', models.DateField(default=datetime.date.today)),
            ],
        ),
        migrations.CreateModel(
            name='StorageTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transno', models.CharField(blank=True, max_length=50, null=True)),
                ('quantity', models.FloatField()),
                ('cost', models.FloatField()),
                ('farmerprice', models.FloatField(blank=True, null=True)),
                ('date', models.DateField(default=datetime.date.today)),
                ('valid', models.BooleanField(default=True)),
                ('invoice', models.FileField(blank=True, null=True, upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='TransactionSale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transno', models.CharField(blank=True, max_length=200, null=True)),
                ('approved', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('1', 'From Produce'), ('2', 'From Warehouse'), ('3', 'From both')], max_length=1)),
                ('quantity', models.FloatField()),
                ('price', models.FloatField()),
                ('invoice', models.FileField(blank=True, null=True, upload_to='')),
            ],
        ),
    ]
