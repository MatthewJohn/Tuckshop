# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_auto_20160125_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='payment_type',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
