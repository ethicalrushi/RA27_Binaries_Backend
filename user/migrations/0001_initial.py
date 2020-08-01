# Generated by Django 2.1.7 on 2020-07-28 11:34

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_auto_20190214_1331'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('name', models.CharField(max_length=300)),
                ('contact', models.CharField(max_length=12)),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('dob', models.DateField(null=True)),
                ('adhaar', models.CharField(max_length=16, null=True, unique=True)),
                ('role', models.CharField(choices=[('FAR', 'Farmer'), ('BUY', 'Buyer'), ('WHO', 'Warehouse Owner'), ('NGO', 'NGO'), ('ADM', 'Admin'), ('DVR', 'Delivery Partner')], max_length=3)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Centre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cid', models.CharField(max_length=200)),
                ('admin', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Demand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField()),
                ('centre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Centre')),
            ],
        ),
        migrations.CreateModel(
            name='Farms',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('farmer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='farms', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FoodGrain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50)),
                ('life', models.IntegerField()),
                ('price', models.IntegerField(default=17)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('xloc', models.FloatField()),
                ('yloc', models.FloatField()),
                ('centre', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='user.Centre')),
            ],
        ),
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('msg', models.TextField()),
                ('seen', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50)),
                ('sector', models.CharField(choices=[('PVT', 'Private'), ('PUB', 'Public')], max_length=3)),
                ('price', models.FloatField(default=20000)),
                ('farmerprice', models.FloatField(blank=True, null=True)),
                ('free_space', models.FloatField()),
                ('total_space', models.FloatField()),
                ('description', models.TextField(blank=True)),
                ('foodgrain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.FoodGrain')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.Location')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warehouses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='farms',
            name='location',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='farms', to='user.Location'),
        ),
        migrations.AddField(
            model_name='demand',
            name='foodgrain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.FoodGrain'),
        ),
        migrations.AddField(
            model_name='centre',
            name='def_crops',
            field=models.ManyToManyField(related_name='d_centre', to='user.FoodGrain'),
        ),
        migrations.AddField(
            model_name='centre',
            name='rec_crops',
            field=models.ManyToManyField(related_name='r_centre', to='user.FoodGrain'),
        ),
    ]
