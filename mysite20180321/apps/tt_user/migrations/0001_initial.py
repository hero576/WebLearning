# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import django.utils.timezone
import django.contrib.auth.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', blank=True, null=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, verbose_name='username', help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')])),
                ('first_name', models.CharField(verbose_name='first name', blank=True, max_length=30)),
                ('last_name', models.CharField(verbose_name='last name', blank=True, max_length=30)),
                ('email', models.EmailField(verbose_name='email address', blank=True, max_length=254)),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False, help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(verbose_name='active', default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
                ('add_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('isDelete', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, to='auth.Group', related_name='user_set', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups', related_query_name='user')),
                ('user_permissions', models.ManyToManyField(blank=True, to='auth.Permission', related_name='user_set', help_text='Specific permissions for this user.', verbose_name='user permissions', related_query_name='user')),
            ],
            options={
                'db_table': 'tt_users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AddrInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('add_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('isDelete', models.BooleanField(default=False)),
                ('receiver', models.CharField(max_length=10)),
                ('addr', models.CharField(max_length=20)),
                ('code', models.CharField(max_length=6)),
                ('phone_number', models.CharField(max_length=11)),
                ('isDefault', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'AddrInfo',
            },
        ),
        migrations.CreateModel(
            name='AreaInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('title', models.CharField(max_length=20)),
                ('aParent', models.ForeignKey(blank=True, to='tt_user.AreaInfo', null=True)),
            ],
            options={
                'db_table': 'tt_area',
            },
        ),
        migrations.AddField(
            model_name='addrinfo',
            name='city',
            field=models.ForeignKey(to='tt_user.AreaInfo', related_name='city'),
        ),
        migrations.AddField(
            model_name='addrinfo',
            name='district',
            field=models.ForeignKey(to='tt_user.AreaInfo', related_name='district'),
        ),
        migrations.AddField(
            model_name='addrinfo',
            name='province',
            field=models.ForeignKey(to='tt_user.AreaInfo', related_name='province'),
        ),
        migrations.AddField(
            model_name='addrinfo',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
