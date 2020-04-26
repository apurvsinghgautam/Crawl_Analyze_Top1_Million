import socket
import ssl
socket.setdefaulttimeout(5)

def check_tls(domain):
	context = ssl.create_default_context()
	try:
		with socket.create_connection((domain, 443)) as sock:
			with context.wrap_socket(sock, server_hostname=domain) as ssock:
				return (ssock.version())
	except: 
		return ('error')

	