# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20151121_1559'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inventorytransaction',
            options={'ordering': ['-timestamp']},
        ),
    ]
