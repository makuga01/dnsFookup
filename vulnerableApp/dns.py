from dnslib import *

def resolve(domain):
    q = DNSRecord.question(domain)
    a = q.send('127.0.0.1', port=53, timeout=1)
    return str(DNSRecord.parse(a).get_a().rdata)
