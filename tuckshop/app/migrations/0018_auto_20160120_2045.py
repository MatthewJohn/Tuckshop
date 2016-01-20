# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_auto_20160120_2004'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockpayment',
            name='fully_paid',
        ),
        migrations.RemoveField(
            model_name='stockpayment',
            name='installment',
        ),
    ]
