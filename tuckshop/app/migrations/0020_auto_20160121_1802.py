# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_auto_20160121_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockpaymenttransaction',
            name='user',
            field=models.ForeignKey(related_name='user', default=1, to='app.User'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='stockpaymenttransaction',
            name='author',
            field=models.ForeignKey(related_name='author', to='app.User'),
        ),
    ]
