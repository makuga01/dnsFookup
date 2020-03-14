from flask_restful import Resource, reqparse
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)

parser = reqparse.RequestParser()
parser.add_argument('username', help = 'This field cannot be blank', required = True)
parser.add_argument('password', help = 'This field cannot be blank', required = True)


from models import UserModel, RevokedTokenModel

class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': 'User already exists', 'error': True}, 500
        elif len(data['password']) <= 7:
            return {'message': 'Password has to be at least 8 chars long', 'error': True}, 500
        new_user = UserModel(
            username = data['username'],
            password = UserModel.generate_hash(data['password'])
        )

        try:
            new_user.save_to_db()
            access_token = create_access_token(identity = data['username'])
            #refresh_token = create_refresh_token(identity = data['username'])
            return {
                'name': data['username'],
                'access_token': access_token,
                #'refresh_token': refresh_token
                }
        except:
            return {'message': 'Something went wrong', 'error': True}, 500


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        current_user = UserModel.find_by_username(data['username'])

        if not current_user:
            return {'message': 'Wrong credentials','error': True}, 500

        if UserModel.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity = data['username'])
            #refresh_token = create_refresh_token(identity = data['username'])
            return {
                'name': current_user.username,
                'access_token': access_token,
                #'refresh_token': refresh_token
                }
        else:
            return {'message': 'Wrong credentials', 'error': True}, 500


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong', 'error': True}

class UserName(Resource):
    @jwt_required
    def get(self):
        return {"name": get_jwt_identity()}

# class UserLogoutRefresh(Resource):
#     @jwt_refresh_token_required
#     def post(self):
#         jti = get_raw_jwt()['jti']
#         try:
#             revoked_token = RevokedTokenModel(jti = jti)
#             revoked_token.add()
#             return {'message': 'Refresh token has been revoked'}
#         except:
#             return {'message': 'Something went wrong', 'error': True}, 500
#
#
# class TokenRefresh(Resource):
#     @jwt_refresh_token_required
#     def post(self):
#         current_user = get_jwt_identity()
#         access_token = create_access_token(identity = current_user)
#         return {'access_token': access_token}
#
