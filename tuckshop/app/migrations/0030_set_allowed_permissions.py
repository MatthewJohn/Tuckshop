
from __future__ import unicode_literals

from django.db import migrations, models
from tuckshop.core.permission import Permission

def set_default_permissions(apps, schema_editor):
    User = apps.get_model('app', 'User')
    for row in User.objects.all():
        permission_bit = 1 << Permission.ACCESS_CREDIT_PAGE.value
        row.permissions |= permission_bit
        permission_bit = 1 << Permission.ACCESS_STOCK_PAGE.value
        row.permissions |= permission_bit
        row.save()

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0029_user_skype_id'),
    ]

    operations = [
        migrations.RunPython(set_default_permissions, reverse_code=migrations.RunPython.noop),
    ]