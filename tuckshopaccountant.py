#!/usr/bin/python

import os
import BaseHTTPServer

from SocketServer import ThreadingMixIn
import threading

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
    server_address = ('', 5000)
    httpd = ThreadedHTTPServer(server_address, RequestHandler)
    httpd.serve_forever()
