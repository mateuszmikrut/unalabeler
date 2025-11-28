"""
DNS lookup tool for easy handling
"""
import socket
import ipaddress

def reverse_lookup(ip):
  """
  Reverse DNS lookup
  """
  try:
    hostname, _, _ = socket.gethostbyaddr(ip)
    return hostname
  except (socket.herror, socket.gaierror, OSError) as e:
    return None

def forward_lookup(name):
  """
  Forward DNS lookup
  """
  try:
    ip = socket.gethostbyname(name)
    return ip
  except (socket.herror, socket.gaierror, OSError) as e:
    return None

def is_valid_ip(value):
  """
  Check if a string is a valid IP address
  """
  try:
    ipaddress.ip_address(value)
    return True
  except ValueError:
    return False

def lookup(host):
  if is_valid_ip(host):
    return reverse_lookup(host)
  else:
    return forward_lookup(host)
