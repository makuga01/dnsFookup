import socket, glob, json
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

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, port))

FAILURE_IP = config['dns']['failure_ip']

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

"""
The following code is from https://github.com/howCodeORG/howDNS
I only changed the getrecs function for DNS rebinding to work
"""


def getflags(flags):

    byte1 = bytes(flags[:1])
    byte2 = bytes(flags[1:2])

    rflags = ""

    QR = "1"

    OPCODE = ""
    for bit in range(1, 5):
        OPCODE += str(ord(byte1) & (1 << bit))

    AA = "1"

    TC = "0"

    RD = "0"

    # Byte 2

    RA = "0"

    Z = "000"

    RCODE = "0000"

    return int(QR + OPCODE + AA + TC + RD, 2).to_bytes(1, byteorder="big") + int(
        RA + Z + RCODE, 2
    ).to_bytes(1, byteorder="big")


def getquestiondomain(data):

    state = 0
    expectedlength = 0
    domainstring = ""
    domainparts = []
    x = 0
    y = 0
    for byte in data:
        if state == 1:
            if byte != 0:
                domainstring += chr(byte)
            x += 1
            if x == expectedlength:
                domainparts.append(domainstring)
                domainstring = ""
                state = 0
                x = 0
            if byte == 0:
                domainparts.append(domainstring)
                break
        else:
            state = 1
            expectedlength = byte
        y += 1

    questiontype = data[y : y + 2]

    return (domainparts, questiontype)


def getrecs(data):
    """
    This function is used to look into redis/SQL and by the uuid (3rd level domain)
    get the IP the domain should resolve to at the moment

    For DNS rebinding to work just this function needed to be changed
    """
    domain, questiontype = getquestiondomain(data)
    qt = ""
    if questiontype == b"\x00\x01":
        qt = "a"

    """
    First check if supplied domain has subdomains (if not resolve 0.0.0.0)

    Create list containing all subdomains requested and
    get uuid from them
    Request format: dig some.random.subdomains.{uuid}.gel0.space
    """
    if len(domain) < 4:
        print(f'{ADDR}:{PORT} {".".join(domain[:-1])} => No subdomain, no fun => {FAILURE_IP}')
        props = [{"name": "", "ttl": 0, "value": FAILURE_IP}]
        return (props, qt, domain)
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
            data = DnsModel.get_props(uuid)["props"]
            setJson(uuid, json.loads(data))
        except:
            print(f'{ADDR}:{PORT} {".".join(domain)[:-1]} (doesn\'t exist) => {FAILURE_IP}')
            props = [{"name": "", "ttl": 0, "value": FAILURE_IP}]
            return (props, qt, domain)

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
    print(f'{ADDR}:{PORT} {".".join(domain)[:-1]} => {resolve_to}')

    new_log = LogModel(
        uuid=uuid,
        domain=".".join(domain)[:-1],
        ip=ADDR,
        port=PORT,
        resolved_to=resolve_to,
        created_date=str(datetime.now()),
    )
    new_log.save_to_db()

    props = [{"name": "", "ttl": 0, "value": resolve_to}]

    return (props, qt, domain)


def buildquestion(domainname, rectype):
    qbytes = b""

    for part in domainname:
        length = len(part)
        qbytes += bytes([length])

        for char in part:
            qbytes += ord(char).to_bytes(1, byteorder="big")

    if rectype == "a":
        qbytes += (1).to_bytes(2, byteorder="big")

    qbytes += (1).to_bytes(2, byteorder="big")

    return qbytes


def rectobytes(domainname, rectype, recttl, recval):

    rbytes = b"\xc0\x0c"

    if rectype == "a":
        rbytes = rbytes + bytes([0]) + bytes([1])

    rbytes = rbytes + bytes([0]) + bytes([1])

    rbytes += int(recttl).to_bytes(4, byteorder="big")

    if rectype == "a":
        rbytes = rbytes + bytes([0]) + bytes([4])

        for part in recval.split("."):
            rbytes += bytes([int(part)])
    return rbytes


def buildresponse(data):

    # Transaction ID
    TransactionID = data[:2]

    # Get the flags
    Flags = getflags(data[2:4])

    # Question Count
    QDCOUNT = b"\x00\x01"

    # Answer Count
    ANCOUNT = b"\x00\x01"

    # Nameserver Count
    NSCOUNT = (0).to_bytes(2, byteorder="big")

    # Additonal Count
    ARCOUNT = (0).to_bytes(2, byteorder="big")

    dnsheader = TransactionID + Flags + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT

    # Create DNS body
    dnsbody = b""

    # Get answer for query
    records, rectype, domainname = getrecs(data[12:])

    dnsquestion = buildquestion(domainname, rectype)

    for record in records:
        dnsbody += rectobytes(domainname, rectype, record["ttl"], record["value"])

    return dnsheader + dnsquestion + dnsbody


while 1:
    data, addr = sock.recvfrom(512)
    ADDR, PORT = addr
    try:
        r = buildresponse(data)
        sock.sendto(r, addr)
    except Exception as e:
        print(f'An exception happened, yes this server isn\'t perfect :D {e}')
