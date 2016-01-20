# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_auto_20160118_0828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockpayment',
            name='inventory_transaction',
            field=models.ForeignKey(to='app.InventoryTransaction', null=True),
        ),
    ]
