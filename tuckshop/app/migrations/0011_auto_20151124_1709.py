# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_auto_20151121_1615'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventory',
            name='price',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='inventory',
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='sale_price',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='inventory_transactions',
            field=models.ForeignKey(to='app.InventoryTransaction', null=True),
        ),
    ]
