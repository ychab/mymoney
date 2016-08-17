# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BankTransactionTag',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='Name', max_length=255)),
                ('owner', models.ForeignKey(related_name='tags', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'db_table': 'banktransactiontags',
            },
        ),
    ]
