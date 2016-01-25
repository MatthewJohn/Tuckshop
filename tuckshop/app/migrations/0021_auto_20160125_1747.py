# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_auto_20160121_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 25, 17, 47, 29, 872626, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 25, 17, 47, 32, 383173, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
