# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_user_shared'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='shared_name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
