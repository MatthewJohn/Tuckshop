# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_user_shared_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='author',
            field=models.ForeignKey(related_name='transaction_author', default=1, to='app.User'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='user',
            field=models.ForeignKey(related_name='transaction_user', to='app.User'),
        ),
    ]
