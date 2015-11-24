# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20151124_1835'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='inventory_transactions',
            new_name='inventory_transaction',
        ),
        migrations.RemoveField(
            model_name='inventory',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='inventorytransaction',
            name='approved',
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='description',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
