# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_auto_20151126_1929'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stockpayment',
            options={'ordering': ['-timestamp']},
        ),
    ]
