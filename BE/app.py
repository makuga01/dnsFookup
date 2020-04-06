from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import psycopg2
from flask_cors import CORS
import yaml

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

"""
*** CONFIG ***
"""

config = yaml.safe_load(open("../config.yaml"))

db_conf = config['sql']

app.config['SQLALCHEMY_DATABASE_URI'] = f"\
{db_conf['protocol']}://\
{db_conf['user']}:{db_conf['password']}\
@{db_conf['host']}\
/{db_conf['db']}\
"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = db_conf['deprec_warn'] # silence the deprecation warning

db = SQLAlchemy(app)

@app.before_first_request
def create_tables():
    db.create_all()

app.config['JWT_SECRET_KEY'] = config['jwt']['secret_key']
jwt = JWTManager(app)

app.config['JWT_BLACKLIST_ENABLED'] = config['jwt']['blacklist_enabled']
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = config['jwt']['blacklist_token_checks']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config['jwt']['token_expires']

"""
*** CONFIG ***
"""

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)

import models, resources, dns_resources

api.add_resource(resources.UserRegistration, '/auth/signup')
api.add_resource(resources.UserLogin, '/auth/login')
api.add_resource(resources.UserLogoutAccess, '/auth/logout')
api.add_resource(resources.ChangePw, '/auth/change_pw')

api.add_resource(dns_resources.iDontWannaBeAnymore, '/auth/delete_me')

api.add_resource(dns_resources.CreateRebindToken, '/api/fookup/new')
api.add_resource(dns_resources.DeleteUUID, '/api/fookup/delete')

api.add_resource(resources.UserName, '/api/user')
api.add_resource(dns_resources.GetUserTokens, '/api/fookup/listAll')
api.add_resource(dns_resources.GetProps, '/api/fookup/props')
api.add_resource(dns_resources.GetUserLogs, '/api/fookup/logs/all')
api.add_resource(dns_resources.GetUuidLogs, '/api/fookup/logs/uuid')
api.add_resource(dns_resources.GetStatistics, '/api/statistics')
