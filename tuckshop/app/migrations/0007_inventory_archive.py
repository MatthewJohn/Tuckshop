# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20151103_2102'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='archive',
            field=models.BooleanField(default=False),
        ),
    ]
