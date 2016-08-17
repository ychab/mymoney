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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, verbose_name='Label')),
                ('date', models.DateField(verbose_name='Date', default=datetime.date.today)),
                ('amount', models.DecimalField(max_digits=10, verbose_name='Amount', decimal_places=2)),
                ('currency', models.CharField(editable=False, max_length=3, verbose_name='Currency')),
                ('status', models.CharField(max_length=32, default='active', verbose_name='Status', help_text='Depending on its value, determine whether it could alter the bank account balance or being used by statistics.', choices=[('active', 'Active'), ('ignored', 'Ignored'), ('inactive', 'Inactive')])),
                ('reconciled', models.BooleanField(verbose_name='Reconciled', help_text='Whether the bank transaction has been applied on the real bank account.', default=False)),
                ('payment_method', models.CharField(max_length=32, default='credit_card', verbose_name='Payment method', choices=[('credit_card', 'Credit card'), ('cash', 'Cash'), ('transfer', 'Transfer'), ('transfer_internal', 'Transfer internal'), ('check', 'Check')])),
                ('memo', models.TextField(blank=True, verbose_name='Memo')),
                ('scheduled', models.BooleanField(editable=False, default=False)),
                ('bankaccount', models.ForeignKey(to='bankaccounts.BankAccount', related_name='banktransactions', on_delete=models.CASCADE)),
                ('tag', models.ForeignKey(related_name='banktransactions', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Tag', to='banktransactiontags.BankTransactionTag', blank=True, null=True)),
            ],
            options={
                'get_latest_by': 'date',
                'db_table': 'banktransactions',
            },
        ),
        migrations.AlterIndexTogether(
            name='banktransaction',
            index_together=set([('bankaccount', 'reconciled'), ('bankaccount', 'date'), ('bankaccount', 'amount')]),
        ),
    ]
