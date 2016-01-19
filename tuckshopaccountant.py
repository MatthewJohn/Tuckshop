#!/usr/bin/python

import os
import BaseHTTPServer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tuckshop.settings")

import django
django.setup()

from tuckshop.page.factory import Factory as PageFactory


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self, post_vars={}):
        page_object = PageFactory.getPageObject(self)
        page_object.processRequest(post_request=False)

    def do_POST(self):
        page_object = PageFactory.getPageObject(self)
        page_object.processRequest(post_request=True)


if (__name__ == '__main__'):

    server_address = ('', 5000)
    httpd = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
    httpd.serve_forever()
