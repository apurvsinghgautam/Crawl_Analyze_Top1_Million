'''
Online test: https://ipv6-test.com/validate.php
Source: https://github.com/danyork/aaaa-check/blob/master/aaaa-check.py

Note: There may be a tradeoff between latency/accuracy that is
	  affected by resolver.timeout and resolver.lifetime values
'''

import socket
import dns.resolver

# Returns True if url is IPv6 reachable, False otherwise
def check(url):
	try:
		ipv = socket.getaddrinfo(url, 80, family=socket.AF_INET6)

		# Query for A, AAAA DNS records
		resolver = dns.resolver.Resolver()
		resolver.timeout = 1
		resolver.lifetime = 1
		answer_A = dns.resolver.query(url, "A")
		answer_AAAA = dns.resolver.query(url, "AAAA")

		# If there is IPv6 address and DNS queries do not fail, return True
		if ipv[0][0].name == "AF_INET6":
			return True

	# Else, socket.getaddrinfo or dns.resolver.query failed somehow
	except (socket.gaierror, dns.resolver.NXDOMAIN,
			dns.resolver.NoAnswer, dns.resolver.NoNameservers,
			dns.exception.Timeout, dns.resolver.YXDOMAIN):
		pass

	return False
