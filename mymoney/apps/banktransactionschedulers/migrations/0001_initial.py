# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('banktransactiontags', '0001_initial'),
        ('bankaccounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankTransactionScheduler',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('label', models.CharField(verbose_name='Label', max_length=255)),
                ('date', models.DateField(verbose_name='Date', default=datetime.date.today)),
                ('amount', models.DecimalField(decimal_places=2, verbose_name='Amount', max_digits=10)),
                ('currency', models.CharField(editable=False, verbose_name='Currency', max_length=3)),
                ('status', models.CharField(verbose_name='Status', choices=[('active', 'Active'), ('ignored', 'Ignored'), ('inactive', 'Inactive')], help_text='Depending on its value, determine whether it could alter the bank account balance or being used by statistics.', default='active', max_length=32)),
                ('reconciled', models.BooleanField(verbose_name='Reconciled', default=False, help_text='Whether the bank transaction has been applied on the real bank account.')),
                ('payment_method', models.CharField(verbose_name='Payment method', choices=[('credit_card', 'Credit card'), ('cash', 'Cash'), ('transfer', 'Transfer'), ('transfer_internal', 'Transfer internal'), ('check', 'Check')], default='credit_card', max_length=32)),
                ('memo', models.TextField(verbose_name='Memo', blank=True)),
                ('type', models.CharField(verbose_name='Type', choices=[('monthly', 'Monthly'), ('weekly', 'Weekly')], help_text='The type of recurrence to be applied.', default='monthly', max_length=32)),
                ('recurrence', models.PositiveSmallIntegerField(null=True, verbose_name='Recurrence', blank=True, help_text='How many time the bank transaction should be cloned.')),
                ('last_action', models.DateTimeField(null=True, editable=False, help_text='Last time the scheduled bank transaction has been cloned.')),
                ('state', models.CharField(editable=False, choices=[('waiting', 'Waiting'), ('finished', 'Finished'), ('failed', 'Failed')], help_text='State of the scheduled bank transaction.', default='waiting', max_length=32)),
                ('bankaccount', models.ForeignKey(to='bankaccounts.BankAccount', related_name='banktransactionschedulers', on_delete=models.CASCADE)),
                ('tag', models.ForeignKey(to='banktransactiontags.BankTransactionTag', null=True, blank=True, verbose_name='Tag', on_delete=django.db.models.deletion.SET_NULL, related_name='banktransactionschedulers')),
            ],
            options={
                'db_table': 'banktransactionschedulers',
            },
        ),
        migrations.AlterIndexTogether(
            name='banktransactionscheduler',
            index_together=set([('state', 'last_action')]),
        ),
    ]
