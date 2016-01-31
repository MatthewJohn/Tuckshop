# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_user_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='shared',
            field=models.BooleanField(default=False),
        ),
    ]
