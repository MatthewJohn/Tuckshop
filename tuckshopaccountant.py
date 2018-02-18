#!/usr/bin/python

import os
import BaseHTTPServer
from raven import Client

from SocketServer import ThreadingMixIn

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


class ThreadedHTTPServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    """Handle requests in a separate thread."""
    pass

if (__name__ == '__main__'):

    client = Client('http://ec8bd0585c2640c0881c3ff84320226d:d574725c931944c79ea0b056d05db850@localhost:8090/2')
    try:
        server_address = ('', 5000)
        httpd = ThreadedHTTPServer(server_address, RequestHandler)
        httpd.serve_forever()
    except:
        client.captureException()
