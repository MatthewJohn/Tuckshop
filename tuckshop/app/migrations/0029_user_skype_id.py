# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_transaction_affect_float'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='skype_id',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
