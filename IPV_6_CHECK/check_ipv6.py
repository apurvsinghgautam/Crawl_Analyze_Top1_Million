import socket
import ssl
import re
import threading
import sys
from urllib.parse import urlparse
import dns.resolver

def check_ipv6(url):
    try:
        resolver = dns.resolver.Resolver()
        try:
            answer_AAAA = dns.resolver.query(url, "AAAA")
        except dns.resolver.NoAnswer:
            return "no"
        return "yes"
    except:
        return "error"
