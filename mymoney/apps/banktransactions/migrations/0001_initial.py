# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bankaccounts', '0001_initial'),
        ('banktransactiontags', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankTransaction',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('label', models.CharField(verbose_name='Label', max_length=255)),
                ('date', models.DateField(default=datetime.date.today, verbose_name='Date')),
                ('amount', models.DecimalField(verbose_name='Amount', max_digits=10, decimal_places=2)),
                ('currency', models.CharField(verbose_name='Currency', editable=False, max_length=3)),
                ('status', models.CharField(default='active', verbose_name='Status', max_length=32, help_text='The bank transaction status could be used to determine if is alter the bank account balance.', choices=[('active', 'Active'), ('inactive', 'Inactive')])),
                ('reconciled', models.BooleanField(default=False, verbose_name='Reconciled', help_text='Whether the bank transaction has been applied on the real bank account.')),
                ('payment_method', models.CharField(default='credit_card', verbose_name='Payment method', max_length=32, choices=[('credit_card', 'Credit card'), ('cash', 'Cash'), ('transfer', 'Transfer'), ('transfer_internal', 'Transfer internal'), ('check', 'Check')])),
                ('memo', models.TextField(verbose_name='Memo', blank=True)),
                ('scheduled', models.BooleanField(default=False, editable=False)),
                ('bankaccount', models.ForeignKey(related_name='banktransactions', to='bankaccounts.BankAccount')),
                ('tag', models.ForeignKey(to='banktransactiontags.BankTransactionTag', verbose_name='Tag', blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='banktransactions', null=True)),
            ],
            options={
                'db_table': 'banktransactions',
                'get_latest_by': 'date',
            },
        ),
        migrations.AlterIndexTogether(
            name='banktransaction',
            index_together=set([('bankaccount', 'reconciled'), ('bankaccount', 'amount'), ('bankaccount', 'date')]),
        ),
    ]
