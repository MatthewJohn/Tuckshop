# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_auto_20160131_2040'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='affect_float',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
