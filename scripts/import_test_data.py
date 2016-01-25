#!/usr/bin/python

import os
import sys
sys.path.append('./')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tuckshop.settings")

import django
django.setup()

from tuckshop.app.models import *
from tuckshop.core.utils import *

if not User.objects.filter(uid='mc'):
    user = User(uid='mc')
    user.save()
else:
    user = User.objects.get(uid='mc')

items = [
    ['Twix', [3, 2], 'https://upload.wikimedia.org/wikipedia/en/thumb/f/f9/Twix-Wrapper-Small.jpg/240px-Twix-Wrapper-Small.jpg'],
    ['Mars Bar', [4], 'http://www.westerngazette.co.uk/images/localworld/ugc-images/276414/Article/images/20800136/5900870-large.jpg'],
    ['KitKat', [6], 'http://www.brandonshelf.com/Wordpress/wp-content/uploads/2015/05/Global-KITKAT-Pack-Shot1.png']
]

for item_itx in items:
    item = Inventory(name=item_itx[0], image_url=item_itx[2])
    item.save()
    for quantity in item_itx[1]:
        InventoryTransaction(inventory=item, user=user, quantity=quantity, cost=(quantity * 10), sale_price=(quantity * 15)).save()
