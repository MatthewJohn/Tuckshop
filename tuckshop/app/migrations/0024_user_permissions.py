# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_change'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='permissions',
            field=models.IntegerField(default=0),
        ),
    ]
