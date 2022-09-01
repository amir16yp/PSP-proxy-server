#!/usr/bin/python3

import socketserver
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from http.client import HTTPMessage
from requests import get
from sys import argv
from urllib.parse import urlparse


class PSPProxyHandler(BaseHTTPRequestHandler):

    site = "https://en.wikipedia.org/"
    domain = "en.wikipedia.org"

    def do_GET(self):
        try:    
            if self.path == "/":
                self.send_response(302)
                self.send_header('Location', '/en.wikipedia.org/')
                self.end_headers()
                return
            elif self.path == '/robots.txt':
                self.send_response(200)
                self.wfile.write("User-agent: *\nDisallow: /\n".encode('utf-8'))
                return 
        
            self.domain = self.path.split('/')[0]
            self.site = "https:/" + self.domain
            response = get(self.site + self.path)

            self.send_response(response.status_code)
            ishtml = False
            # add all headers from the original request
            # except for content-encoding, we are forcing utf-8
            to_exclude = ["Content-Encoding", 'Referer', 'Host']
            for x in to_exclude:
                try:
                    response.headers.pop(to_exclude)
                except Exception as e:
                    pass
                try:
                    response.headers.pop(to_exclude.lower())
                except Exception as e:
                    pass
            if "Content-Type" in response.headers.keys():
                if 'text/html' in response.headers["Content-Type"].lower():
                    ishtml = True
            if "content-type" in response.headers.keys():
                if 'text/html' in response.headers["content-type"].lower():
                    ishtml = True
        
            self.end_headers()
            
            if ishtml:
                print("html: true")
                html = response.content.decode()
                print(response.url)
                new_url = urlparse(response.url).netloc
                print(new_url)
                html = html.replace('href="', 'href="/' + new_url + '/')
                html = html.replace("href=/", "href='/" + new_url + '/')
            
                html = html.replace('src="', 'src="/' + new_url + '/')
                html = html.replace("src='", "src='/" + new_url + '/')

                html = html.replace('src="/' + new_url + '///', 'src="/')
                html = html.replace("src='" + new_url + '///', "src='/")


                self.wfile.write(html.encode('utf-8'))
            else:
                self.wfile.write(response.content)
        except Exception as e:
            print("WARNING: " + str(e))
if __name__ == "__main__":
    if len(argv) <= 1:
        print("Please specify port number!")
        exit()
    httpd = socketserver.TCPServer(("", int(argv[1])), PSPProxyHandler)
    httpd.serve_forever()
