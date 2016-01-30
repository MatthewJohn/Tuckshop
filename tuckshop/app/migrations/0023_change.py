# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_transaction_payment_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Change',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('object_type', models.CharField(max_length=255)),
                ('object_id', models.IntegerField()),
                ('changed_field', models.CharField(max_length=255)),
                ('previous_value', models.CharField(max_length=255)),
                ('new_value', models.CharField(max_length=255)),
                ('user', models.ForeignKey(to='app.User')),
            ],
        ),
    ]
