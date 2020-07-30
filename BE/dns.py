import sys
import time
import threading
import traceback
import socketserver as SocketServer
from dnslib import *
import json
from redis import StrictRedis
from app import db
from datetime import datetime
import yaml

"""
*** CONFIG ***
"""

config = yaml.safe_load(open("../config.yaml"))

port = config['dns']['port']
ip = config['dns']['ip']

USE_FAILURE = config['dns']['use_failure_ip']
FAILURE_IP = config['dns']['failure_ip']
host_domain = config['dns']['domain']
use_fail_ns = config['dns']['use_fail_ns']
fail_ns = config['dns']['fail_ns']

redis_config = {
  'host': config['redis']['host'],
  'port': config['redis']['port'],
  'password': config['redis']['password']
}
REDIS_EXP = config['redis']['expiration'] #seconds
redis = StrictRedis(socket_connect_timeout = config['redis']['timeout'],**redis_config)

"""
*** CONFIG ***
"""

"""
SQLAlchemy models for easier access to database
"""


class DnsModel(db.Model):
    db.metadata.clear()
    __tablename__ = "dns_tokens"
    extend_existing = True
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=False, nullable=False)
    uuid = db.Column(db.String(120), unique=True, nullable=False)
    props = db.Column(db.String(2056), unique=False, nullable=False)

    @classmethod
    def get_props(cls, uuid):
        def to_json(x):
            return {"username": x.username, "props": x.props}

        return list(map(lambda x: to_json(x), cls.query.filter_by(uuid=uuid)))[0]


class LogModel(db.Model):
    db.metadata.clear()
    __tablename__ = "dns_logs"
    extend_existing = True
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(64), unique=False, nullable=False)
    resolved_to = db.Column(db.String(253), unique=False, nullable=False)
    domain = db.Column(db.String(253), unique=False, nullable=False)
    ip = db.Column(db.String(120), unique=False, nullable=False)
    port = db.Column(db.String(32), unique=False, nullable=False)
    created_date = db.Column(db.String(128), unique=False, nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


"""
Lambda functions used for easier manipulation with redis
"""

setJson = lambda uid, data: redis.setex(uid, REDIS_EXP, json.dumps(data))
getJson = lambda uid: json.loads(redis.get(uid))

def gen_nxdomain_reply(request):
        # Stolen from https://github.com/major1201/dns-router/blob/master/dns-router.py

        reply = request.reply()
        reply.header.rcode = getattr(RCODE, 'NXDOMAIN')
        return reply

def getResType(type):
    """
    This function returns dnslib function and value of record type necessary for creating valid dns answer

    Note for myself/someone other working on this
    Quick script to determine values for dns answer associated with record types
    for i in range(255):
        try:
             print(QTYPE[i], i)
        except: pass
    """
    types = {
        "A": (1,A),
        "AAAA": (28, AAAA),
        "CNAME": (5, CNAME)
    }
    return(types[type])

def buildResponse(d, ADDR, PORT):
    """
    This function is used to look into redis/SQL and by the uuid (3rd level domain)
    get the IP the domain should resolve to at the moment
    """

    data = DNSRecord.parse(d)
    qtype = QTYPE[data.q.qtype]
    domain = str(data.q.qname).split('.')
    rtype = 1 # A
    reply = DNSRecord(DNSHeader(id=data.header.id, qr=1, aa=1, ra=1), q=data.q)
    fail_reply = reply if USE_FAILURE else gen_nxdomain_reply(data)
    """
    First check if supplied domain has subdomains (if not resolve to FAILURE_IP)

    Create list containing all subdomains requested and
    get uuid from them
    Request format: dig some.random.subdomains.{uuid}.gel0.space
    """

    if '.'.join(domain[-3:-1]) != host_domain and use_fail_ns:
        print(f'{str(datetime.now())} - {ADDR}:{PORT} {".".join(domain[-3:-1])} is not my thing NS => {fail_ns}')
        fail_reply.add_answer(RR(rname = '.'.join(domain), rtype = 2, rclass = 1, rdata = NS(fail_ns)))
        return fail_reply.pack()

    if len(domain) < 4:
        print(f'{str(datetime.now())} - {ADDR}:{PORT} {".".join(domain[:-1])} => No subdomain, no fun => {FAILURE_IP if USE_FAILURE else "NXDOMAIN"}')

        fail_reply.add_answer(RR(rname = '.'.join(domain), rtype = rtype, rclass = 1, rdata = A(FAILURE_IP))) if USE_FAILURE else 0
        return fail_reply.pack()
    subs = domain[:-3]
    uuid = subs[-1]

    """
    Check for uuid in redis
    If uuid is not present (doesn't exist or expired) it checks
    if the uuid is in database and tries to load it back to redis
    If the uuid doesn't exist the dns query will resolve to 0.0.0.0,
    script will print what's happening and the life goes on...
    """
    if not redis.exists(uuid):
        try:
            props = DnsModel.get_props(uuid)["props"]
            setJson(uuid, json.loads(props))
        except:
            print(f'{str(datetime.now())} - {ADDR}:{PORT} {".".join(domain)[:-1]} (doesn\'t exist) => {FAILURE_IP if USE_FAILURE else "NXDOMAIN"}')
            fail_reply.add_answer(RR(rname = '.'.join(domain), rtype = rtype, rclass = 1, rdata = A(FAILURE_IP))) if USE_FAILURE else 0
            return fail_reply.pack()

    """
    Get info about uuid from redis
    """
    rbnd_json = getJson(uuid)

    """
    Turn value increments everytime request to dns server is made

    repeat = How many times this IP should be repetatively resolved
    can be '4ever' or int number of repeats
    Then check if repeat is '4ever' or integer
    """
    rbnd_json["turn"] += 1
    repeat = rbnd_json["ip_props"][rbnd_json["ip_to_resolve"]]["repeat"]

    if repeat == "4ever" or type(repeat) != int:
        """
        Do nothing when rebinding forever or
        when an invalid repeat value is somehow supplied
        """
        pass
    elif rbnd_json["turn"] >= repeat:
        """
        Reset turn value and move on to next IP
        """
        rbnd_json["turn"] = 0
        rbnd_json["ip_to_resolve"] = (
            str(int(rbnd_json["ip_to_resolve"]) + 1)
            if len(rbnd_json["ip_props"]) != int(rbnd_json["ip_to_resolve"])
            else "1"
        )
        setJson(uuid, rbnd_json)
    else:
        """
        If nothing special is happening just save data with incremented turn back to redis
        """
        setJson(uuid, rbnd_json)

    """
    Print what was requested and the ip server responds with
    Log this data into db
    Aaaand finally return the data
    """
    resolve_to = rbnd_json["ip_props"][rbnd_json["ip_to_resolve"]]["ip"]
    answer_type = rbnd_json["ip_props"][rbnd_json["ip_to_resolve"]].get("type")
    now = str(datetime.now())
    print(f'{now} - {ADDR}:{PORT} {answer_type if answer_type else "A"} {".".join(domain)[:-1]} => {resolve_to}')

    rtype, rfunc = getResType(answer_type) if answer_type else (1, A)

    new_log = LogModel(
        uuid=uuid,
        domain=".".join(domain)[:-1],
        ip=ADDR,
        port=PORT,
        resolved_to=resolve_to,
        created_date=now,
    )
    new_log.save_to_db()

    print(resolve_to)
    reply.add_answer(RR(rname = '.'.join(domain), rtype = rtype, rclass = 1, rdata = rfunc(resolve_to)))
    return reply.pack()

# Stolen:
# https://gist.github.com/andreif/6069838

class BaseRequestHandler(SocketServer.BaseRequestHandler):

    def get_data(self):
        raise NotImplementedError

    def send_data(self, data):
        raise NotImplementedError

    def handle(self):
        ADDR, PORT = self.client_address

        try:
            data = self.get_data()
            self.send_data(buildResponse(data, ADDR, PORT))
        except Exception:
            traceback.print_exc(file=sys.stderr)


class TCPRequestHandler(BaseRequestHandler):
    # A bit modified since the original code errors out in python3.7
    def get_data(self):
        data = self.request.recv(8192).strip()
        sz = int(data[:2].hex(), 16)
        if sz < len(data) - 2:
            raise Exception("Wrong size of TCP packet")
        elif sz > len(data) - 2:
            raise Exception("Too big TCP packet")
        return data[2:]

    def send_data(self, data):
        sz = hex(len(data))[2:].zfill(4)
        return self.request.sendall(bytes.fromhex(sz) + data)


class UDPRequestHandler(BaseRequestHandler):

    def get_data(self):
        return self.request[0].strip()

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)


if __name__ == '__main__':
    print("DNS server warming up!")

    servers = [
        SocketServer.ThreadingUDPServer((ip, port), UDPRequestHandler),
        SocketServer.ThreadingTCPServer((ip, port), TCPRequestHandler),
    ]
    for s in servers:
        thread = threading.Thread(target=s.serve_forever)  # that thread will start one more thread for each request
        thread.daemon = True  # exit the server thread when the main thread terminates
        thread.start()
        print("%s server loop running in thread: %s" % (s.RequestHandlerClass.__name__[:3], thread.name))

    try:
        while 1:
            time.sleep(1)
            sys.stderr.flush()
            sys.stdout.flush()

    except KeyboardInterrupt:
        pass
    finally:
        for s in servers:
            s.shutdown()
