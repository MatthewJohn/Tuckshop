# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20151031_0155'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionhistory',
            name='inventory',
            field=models.ForeignKey(to='app.Inventory', null=True),
        ),
    ]
