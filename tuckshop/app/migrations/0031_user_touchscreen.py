# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from tuckshop.app.models import User


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0030_set_allowed_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='touchscreen',
            field=models.BooleanField(default=False),
        ),
    ]

    def apply(self, *args, **kwargs):
        return_value = super(Migration, self).apply(*args, **kwargs)
        for user in User.objects.all():
            user.touchscreen = bool(user.skype_id)
            user.save()
        return return_value
