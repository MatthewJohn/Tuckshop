# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20151121_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventorytransaction',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 21, 15, 59, 47, 304522, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
