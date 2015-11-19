# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20151031_0314'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField()),
                ('cost', models.DecimalField(max_digits=4, decimal_places=2)),
            ],
        ),
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ['-timestamp']},
        ),
        migrations.RenameField(
            model_name='inventory',
            old_name='sale_price',
            new_name='price',
        ),
        migrations.RemoveField(
            model_name='inventory',
            name='cost',
        ),
        migrations.AddField(
            model_name='inventory',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='inventory',
            field=models.ForeignKey(to='app.Inventory'),
        ),
        migrations.AddField(
            model_name='inventorytransaction',
            name='user',
            field=models.ForeignKey(to='app.User'),
        ),
    ]
