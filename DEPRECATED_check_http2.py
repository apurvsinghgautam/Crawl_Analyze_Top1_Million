'''
Online test: https://tools.keycdn.com/http2-test
Source: https://geekflare.com/python-script-http2-test/

Note: There may be a tradeoff between latency/accuracy that is
	  affected by socket.setdefaulttimeout value
'''

import socket
import ssl
from urllib.parse import urlparse

socket.setdefaulttimeout(5)

# Returns True if site has adopted HTTP/2.0, False otherwise
def check(url):
	try:
		HOST = urlparse("http://www."+url).netloc
		PORT = 443

		context = ssl.create_default_context()
		context.set_alpn_protocols(['h2', 'spdy/3', 'http/1.1'])

		connection = context.wrap_socket(
			socket.socket(socket.AF_INET, socket.SOCK_STREAM),
			server_hostname=HOST)
		connection.connect((HOST, PORT))

		if connection.selected_alpn_protocol() == "h2":
			return True

	except Exception:
		pass

	return False

