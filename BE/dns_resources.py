from flask_restful import Resource, reqparse
from models import UserModel, RevokedTokenModel, DnsModel, LogModel
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
import json
from uuid import uuid4
from redis import StrictRedis
from validators.ip_address import ipv4, ipv6
from validators.domain import domain as checkDomain
from jsonschema import validate
import jsonschema.exceptions
import yaml

"""
*** CONFIG ***
"""

config = yaml.safe_load(open("../config.yaml"))

DOMAIN = config['dns']['domain']

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
For easier manipulation with redis
"""
setJson = lambda uid, data: redis.setex(uid, REDIS_EXP, json.dumps(data))
getJson = lambda uid: json.loads(redis.get(uid))



def checkKeys(lst):
    good = True
    for i in range(1,len(lst)+1):
            if str(i) in lst:
                    pass
            else:
                    good = good and False
    return good

class CreateRebindToken(Resource):
    @jwt_required
    def post(self):
        """
        This function creates new rebind subdomain from json looking something like this:
        {
            "ip_props": {
                "1":{ # <= Order in which domains will be resolved
                    "ip": "88.23.99.110", # <= ip to resolve
                    "repeat": 3 # <= how many times
                }
                "2":{
                    "ip": "169.254.169.254",
                    "repeat": "4ever" # <= forever can be supplied to never stop resolving this domain
                }
            },
            "name": "rbnd_test" # <= name (useful in web ui)
        }

        And half of the code just checks if input is correct if someone reading this has an
        idea how to do it more efficently please contribute
        """
        parser = reqparse.RequestParser()
        parser.add_argument('ip_props', help = 'This field cannot be blank wtf', required = True, location="json")
        parser.add_argument('name', help = 'This field cannot be blank wtf', required = True, location="json")
        req_data = parser.parse_args()

        """
        req_data['ip_props'] is a json in string so I need to load it :D
        """
        data = json.loads(req_data['ip_props'].replace('\'', '"'))

        """
        Validate input against base_schema
        """
        req_data['ip_props'] = data
        base_schema = {
            "type": "object",
            "properties": {
                "ip_props": {"type": "object"},
                "name": {
                    "type": "string",
                    "maxLength": 120
                }
            }
        }

        try:
            validate(instance=req_data, schema=base_schema)
        except jsonschema.exceptions.ValidationError:
            return {'message': 'Something went wrong, the supplied input doesn\'t seem to be valid'}, 500


        """
        Check if
        - Less than 32 IPs are supplied
        - Some retard can't count
        """
        if not len(data.keys())<32:
            return {'message': 'Something went wrong, max IPs: 32'}, 500
        elif not checkKeys(data.keys()):
            return {'message': f"Something went wrong, the str(numbers) go like this: ['1','2','3','4',...] and not {[x for x in data.keys()]}"}, 500

        """
        Iterate through every ip_prop and do some checks - details are in comments below
        """

        for i in data.keys():
            """
            This schema checks if
            - repeat is "4ever" or integer greater or equal to 1
            - ip and type is compatibile with one of A,AAAA and CNAME
            """

            prop_schema = {
                "type": "object",
                "properties": {
                    "repeat": {
                        "anyOf": [
                             {
                                "type": "integer",
                                "minimum": 1
                            },
                            {
                                "type": "string",
                                "pattern": "^4ever$"
                            }
                        ]
                    },
                    "ip": {
                        "type": "string",
                        "anyOf": [
                            {"format": "ipv4"},
                            {"format": "ipv6"},
                            {"format": "idn-hostname"}
                        ]
                    },
                    "type": {
                        "type": "string",
                        "anyOf": [
                            {"pattern": "^A$"},
                            {"pattern": "^AAAA$"},
                            {"pattern": "^CNAME$"}
                        ]
                    }
                }
            }

            try:
                validate(instance=data[i], schema=prop_schema)
            except jsonschema.exceptions.ValidationError:
                return {'message': f'Something went wrong, the supplied input doesn\'t seem to be valid in [`ip_props`][{int(i)-1}]'}, 500

            """
            Check if supplied record type matches ip
            So 127.0.0.1 can't be CNAME
            And google.com can't be answer for A :D
            """
            record_funcs = {
                "CNAME": checkDomain,
                "A": ipv4,
                "AAAA": ipv6
            }
            if not record_funcs[data[i]['type']](data[i]['ip']):
                return {'message': f"data[{int(i)-1}]['ip'] has to be in {data[{int(i)-1}]['type']} format"}, 500


        """
        Then put the data together
        Generate new uuid4
        Put it in database and redis
        Then return the whole domain
        """

        # rbnd_json does not need name parameter - it's meant to be stored in redis and in props column in database
        rbnd_json = {
            'ip_props': data,
            'ip_to_resolve': '1',
            'turn': -1
        }
        uuid = uuid4().hex
        if DnsModel.find_by_uuid(uuid):
            """
            Just in case something bad happens
            """
            return {'message': 'An error occured, please try again (REALLY TRY AGAIN, server generated uuid that exists, I didn\'t know it was possible :d) If you get this error please send it to me on twitter @marek_geleta You can follow me too'}, 500

        new_uuid = DnsModel(
            username = get_jwt_identity(),
            uuid = uuid,
            props = json.dumps(rbnd_json),
            name = req_data['name']
        )

        try:
            new_uuid.save_to_db()
            setJson(uuid, rbnd_json)
            return {"subdomain": f"{uuid}.{DOMAIN}"}
        except:
            return {'message': 'Something went wrong'}, 500

class GetUserTokens(Resource):
    @jwt_required
    def get(self):
        """
        returns all dns tokens owned by a logged in user
        """
        return DnsModel.find_by_user(get_jwt_identity())

class GetProps(Resource):
    @jwt_required
    def post(self):
        """
        returns info about dns token
        looks something like this:
        {
            "ip_props": {
                "1": {
                    "ip": "1.0.0.0",
                    "repeat": 1,
                    "type": "A"
                },
                "2": {
                    "ip": "2.0.0.0",
                    "repeat": 1,
                    "type": "A"
                }
            },
            "ip_to_resolve": "1",
            "turn": -1, # when new webhook is created the turn is on -1
            "name": "something"
        }
        """
        parser = reqparse.RequestParser()
        parser.add_argument('uuid', help = 'This field cannot be blank', required = True, location="json")
        args = parser.parse_args()
        uuid = args['uuid']
        data = DnsModel.get_props(uuid, get_jwt_identity())
        if data:
            data['props'] = json.loads(data['props'])
            data['props']['name'] = data['name']
            return data['props']
        return {"msg": "An error occured"}

class GetUserLogs(Resource):
    @jwt_required
    def get(self):
        """
        Returns all user logs :O
        """
        return LogModel.return_all(get_jwt_identity())

class GetUuidLogs(Resource):
    @jwt_required
    def post(self):
        """
        Returns logs of supplied token
        (owner of the token must be logged in :D)
        """
        parser = reqparse.RequestParser()
        parser.add_argument('uuid', help = 'This field cannot be blank', required = True)
        parser.add_argument('page', help = 'This field cannot be blank', required = False)
        args = parser.parse_args()
        page = int(args['page']) if args['page'] else 1
        entries, pages, data = LogModel.uuid_logs(args['uuid'], get_jwt_identity(), page=page)
        return {'pages': pages, 'data': data, 'entries': entries}

class DeleteUUID(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uuid', help = 'This field cannot be blank', required = True)
        uuid = parser.parse_args()['uuid']
        rds_delet = redis.delete(uuid)
        print("*"*20)
        print(rds_delet)
        print("*"*20)
        uuid_logs = LogModel.delete_by_uuid(uuid, get_jwt_identity())
        uuid_props = DnsModel.delete_by_uuid(uuid, get_jwt_identity())
        return {'uuid_props': uuid_props , 'uuid_logs': uuid_logs}

class GetStatistics(Resource):
    """
    Returns user statistics
    used in /dashboard in FE

    {
    "request_count": 1337,
    "created_bins": 69
    }

    """
    @jwt_required
    def get(self):
        return LogModel.statistics_count(get_jwt_identity())

class iDontWannaBeAnymore(Resource):
    """
    Deletes all tokens and logs then finally the user him(or her)self
    """
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('password', help = 'This field cannot be blank', required = True)
        args = parser.parse_args()

        current_user = UserModel.find_by_username(get_jwt_identity())

        if not current_user or not UserModel.verify_hash(args['password'], current_user.password):
            return {'message': 'Wrong credentials','success': False}

        del_logs = LogModel.delete_by_user(get_jwt_identity())
        del_bins = DnsModel.delete_by_user(get_jwt_identity())
        del_user = UserModel.delete_user(get_jwt_identity())


        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {
                'message': 'Access token has been revoked',
                'total_deleted_rows': {
                    "logs": del_logs,
                    "bins": del_bins,
                    "user": del_user
                },
                'success': True
            }
        except:
            return {'message': 'Something went wrong', 'success': False}
