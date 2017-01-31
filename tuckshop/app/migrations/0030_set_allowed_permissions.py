
from __future__ import unicode_literals

from django.db import migrations, models
from tuckshop.core.permission import Permission

def set_default_permissions(apps, schema_editor):
    User = apps.get_model('app', 'User')
    for row in User.objects.all():
        row.add_permission(Permission.ACCESS_CREDIT_PAGE)
        row.add_permission(Permission.ACCESS_STOCK_PAGE)

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0029_user_skype_id'),
    ]

    operations = [
        migrations.RunPython(set_default_permissions, reverse_code=migrations.RunPython.noop),
    ]