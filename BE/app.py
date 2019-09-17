from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import psycopg2
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

"""
*** CONFIG ***
"""

DB_URL = 'postgresql+psycopg2://postgres:CHANGETHISTOO@localhost/dnsfookup'

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning


db = SQLAlchemy(app)

@app.before_first_request
def create_tables():
    db.create_all()

app.config['JWT_SECRET_KEY'] = 'U(RH*3y328u$#ibf*YGRIBFJ)IHF(**^#@&!)'
jwt = JWTManager(app)

app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']#, 'refresh]
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 60*60*6 # 6 hours

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
api.add_resource(dns_resources.CreateRebindToken, '/api/fookup/new')
api.add_resource(resources.UserName, '/api/user')
api.add_resource(dns_resources.GetUserTokens, '/api/fookup/listAll')
api.add_resource(dns_resources.GetProps, '/api/fookup/props')
api.add_resource(dns_resources.GetUserLogs, '/api/fookup/logs/all')
api.add_resource(dns_resources.GetUuidLogs, '/api/fookup/logs/uuid')
api.add_resource(dns_resources.GetStatistics, '/api/statistics')
