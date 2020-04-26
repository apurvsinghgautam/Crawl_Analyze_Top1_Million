import socket
import ssl
import re
import threading
import sys
from urllib.parse import urlparse

socket.setdefaulttimeout(20)

def check_http2(domain):
    try:
        if 'www' in domain:
            host = urlparse("http://" + domain).netloc
        else:
            host = urlparse("http://www." + domain).netloc
        port = 443
        context = ssl.create_default_context()
        context.set_alpn_protocols(['h2', 'spdy/3', 'http/1.1'])
        connection = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=host)
        connection.connect((host, port))
    except ssl.CertificateError:
        err = str(sys.exc_info())
        err = err.split("doesn't match ")[1]
        if "either" in err:
            err = err.split("either of ")[1]
        p = re.compile('\'(.+?)\'"')
        m = p.match(err)
        try:
            host, port = m.group(1), 443
            context = ssl.create_default_context()
            context.set_alpn_protocols(['h2', 'spdy/3', 'http/1.1'])
            connection = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=host)
            connection.connect((host, port))
        except:
            print(domain, str(sys.exc_info()).split("<class ")[1].split(">,")[0])
            return "error"
    except:
        print(domain, str(sys.exc_info()).split("<class ")[1].split(">,")[0])
        return "error"
    if connection.selected_alpn_protocol() == 'h2':
        return "yes"
    return "no"

# print(check_http2('macys.com'))
