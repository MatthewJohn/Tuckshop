# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_inventory_archive'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='price',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='inventorytransaction',
            name='cost',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='user',
            name='credit',
            field=models.IntegerField(default=0),
        ),
    ]
