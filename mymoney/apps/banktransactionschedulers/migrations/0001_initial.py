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
            name='BankTransactionScheduler',
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
                ('type', models.CharField(default='monthly', verbose_name='Type', max_length=32, help_text='The type of recurrence to be applied.', choices=[('monthly', 'Monthly'), ('weekly', 'Weekly')])),
                ('recurrence', models.PositiveSmallIntegerField(verbose_name='Recurrence', blank=True, help_text='How many time the bank transaction should be cloned.', null=True)),
                ('last_action', models.DateTimeField(editable=False, help_text='Last time the scheduled bank transaction has been cloned.', null=True)),
                ('state', models.CharField(default='waiting', editable=False, max_length=32, help_text='State of the scheduled bank transaction.', choices=[('waiting', 'Waiting'), ('finished', 'Finished'), ('failed', 'Failed')])),
                ('bankaccount', models.ForeignKey(related_name='banktransactionschedulers', to='bankaccounts.BankAccount')),
                ('tag', models.ForeignKey(to='banktransactiontags.BankTransactionTag', verbose_name='Tag', blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='banktransactionschedulers', null=True)),
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
