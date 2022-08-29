#!/usr/bin/python3

import socketserver
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from http.client import HTTPMessage
from requests import get
from sys import argv

global site
site = "https://en.wikipedia.org/"


class PSPProxyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path != '/' or 'favicon.ico' not in self.path:

            response = get(site + self.path)

            self.send_response(response.status_code)
            
            # add all headers from the original request
            # except for content-encoding, we are forcing utf-8
            for h in response.headers.keys():
                if h.lower() not in ["content-encoding"]:
                    self.send_header(h, response.headers[h])
            self.end_headers()

            # return the html
            # this will produce errors in the console, you can safely ignore them
            # TODO: add try and catch and only turn those errors into warnings
            self.wfile.write(response.content.decode().replace('src="//', 'src="http://').replace(
                "src='//", "src='http://").replace('https://', 'http://').encode('utf-8'))
            # for some reason wikipedia's html uses "\\<domain name>" instead of "https://<domain name>" when linking to images


if __name__ == "__main__":
    if len(argv) <= 1:
        print("Please specify port number!")
        exit()
    httpd = socketserver.TCPServer(("", int(argv[1])), PSPProxyHandler)
    httpd.serve_forever()
