# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_transaction_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.IntegerField()),
                ('fully_paid', models.BooleanField(default=False)),
                ('installment', models.BooleanField(default=False)),
                ('description', models.CharField(max_length=255, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='inventorytransaction',
            name='paid',
        ),
        migrations.AddField(
            model_name='stockpayment',
            name='inventory_transaction',
            field=models.ForeignKey(to='app.InventoryTransaction'),
        ),
        migrations.AddField(
            model_name='stockpayment',
            name='user',
            field=models.ForeignKey(to='app.User'),
        ),
    ]
