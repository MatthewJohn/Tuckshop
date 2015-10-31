# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_transactionhistory_inventory'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=5, decimal_places=2)),
                ('debit', models.BooleanField(default=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('inventory', models.ForeignKey(to='app.Inventory', null=True)),
                ('user', models.ForeignKey(to='app.User')),
            ],
        ),
        migrations.RemoveField(
            model_name='transactionhistory',
            name='inventory',
        ),
        migrations.RemoveField(
            model_name='transactionhistory',
            name='user',
        ),
        migrations.DeleteModel(
            name='TransactionHistory',
        ),
    ]
