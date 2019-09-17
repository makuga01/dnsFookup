from flask_restful import Resource, reqparse
from models import UserModel, RevokedTokenModel, DnsModel, LogModel
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
import json
from uuid import uuid4
from redis import StrictRedis
from IPy import IP

"""
*** CONFIG ***
"""
DOMAIN = "gel0.space"

redis_config = {
  'host': '127.0.0.1',
  'port': 6379,
  'password': 'CHANGETHISPW'
}
REDIS_EXP = 60*60 #seconds
redis = StrictRedis(socket_connect_timeout=3,**redis_config)

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
        Check if
        - Less than 32 IPs are supplied
        - Some retard can't count
        - Name is not longer than 64
        """
        if not len(data.keys())<32:
            return {'message': 'Something went wrong, max IPs: 32'}, 500
        elif not checkKeys(data.keys()):
            return {'message': f"Something went wrong, the str(numbers) go like this: ['1','2','3','4',...] and not {[x for x in data.keys()]}"}, 500
        elif len(req_data['name']) > 64:
            return {'message': 'Something went wrong, max name len: 64'}, 500

        """
        Iterate through every ip_prop and check
        """
        for i in data.keys():
            """
            If repeat
            - Is "4ever" or positive integer
            - Is not 0 - kind of makes no sense to repeat it 0 times
            """
            if (data[i]['repeat'] != '4ever' and type(data[i]['repeat']) != int) or abs(data[i]['repeat']) != data[i]['repeat']:
                repeat = data[i]['repeat']
                return {'message': f'Something went wrong, `repeat` field can only hold positive integers or string `4ever` (in [`ip_props`][{i}][`repeat`])'}, 500
            elif data[i]['repeat'] == 0:
                return {'message': f'How am I supposed to repeat it 0 times??? [`ip_props`][{i}][`repeat`]'}, 500

            """
            If ip
            - Is in IPV4 format and if it's not a subnet
            because the IP function is a bit weird and idk what to use :D
            """
            try:
                if IP(data[i]['ip']).version() == 4 and IP(data[i]['ip']).strNormal(0) == str(IP(data[i]['ip'])):
                    data[i]['ip'] = IP(data[i]['ip']).strNormal(0)
                else:
                    return {'message': 'IP has to be in IPV4 format'}, 500

            except:
                return {'message': f'An error occured, check [`ip_props`][{i}][`ip`] '}, 500

        """
        Then put the data together
        Generate new uuid4
        Put it in database and redis
        Then return the whole domain
        """
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
                    "repeat": 1
                },
                "2": {
                    "ip": "2.0.0.0",
                    "repeat": 1
                }
            },
            "ip_to_resolve": "1",
            "turn": -1, # when new webhook is created the turn is on -1
            "name": "something"
        }
        """
        parser = reqparse.RequestParser()
        parser.add_argument('uuid', help = 'This field cannot be blank', required = True, location="json")
        uuid = parser.parse_args()['uuid']
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
        uuid = parser.parse_args()['uuid']
        return LogModel.uuid_logs(uuid, get_jwt_identity())

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
