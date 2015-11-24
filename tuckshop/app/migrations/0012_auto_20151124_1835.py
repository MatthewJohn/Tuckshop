# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_auto_20151124_1709'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='credit',
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='paid',
            field=models.IntegerField(default=0),
        ),
    ]
