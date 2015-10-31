# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_inventory_transactionhistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token_value', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='credit',
            field=models.DecimalField(default=0, max_digits=5, decimal_places=2),
        ),
        migrations.AddField(
            model_name='token',
            name='user',
            field=models.ForeignKey(to='app.User'),
        ),
    ]
