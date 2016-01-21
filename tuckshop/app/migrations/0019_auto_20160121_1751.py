# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_auto_20160120_2045'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockPaymentTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(to='app.User')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddField(
            model_name='stockpayment',
            name='stock_payment_transaction',
            field=models.ForeignKey(default=1, to='app.StockPaymentTransaction'),
            preserve_default=False,
        ),
    ]
