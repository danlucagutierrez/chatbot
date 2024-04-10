from flask import Flask, request, jsonify
import os
import time
import random
import string
from pymongo import MongoClient
from utils.db_manager import DBManager

class AuthService:
    def __init__(self, db: DBManager) -> None:
        self.db = db
        self.app = Flask(__name__)
        self.setup_routes()
    
    def start(self):
        self.app.run(port=5000)

    def stop(self):
        raise SystemExit()

    def setup_routes(self):
        # Define a function to add CORS headers to responses
        @self.app.after_request
        def add_cors_headers(response):
            response.headers['Access-Control-Allow-Origin'] = '*'  # Allow requests from this origin
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'  # Allow Content-Type header
            response.headers['Access-Control-Allow-Methods'] = 'POST'  # Allow POST requests
            return response

        @self.app.route('/api/validateLink/', methods=['POST'])
        def validate_url():
            data = request.json
            user_id = data['id']
            token = data['token']
            user = self.db.get_user(user_id)
            if user == None or not self.validate_token(user, token):
                print('Invalid token or user while validating url')
                return jsonify({'isValid': False})
            tk_use = user['tk_use']
            print('Valid url')
            return jsonify({
                'isValid': True,
                'createNewCredential': tk_use == 'register',
                'credentialOptions': self.get_credential_options(tk_use, user)
            })

        @self.app.route('/api/authenticateKey/', methods=['POST'])
        def authenticate_key():
            data = request.json
            user_id = data['id']
            token = data['token']
            publicKey = data['key']
            user = self.db.get_user(user_id)
            if user == None or not self.validate_token(user, token):
                print('Invalid token or user while authing')
                return jsonify({'isValid': False})
            tk_use = user['tk_use']
            if tk_use == 'login':
                if not self.validate_key(user, publicKey):
                    return jsonify({'isValid': False})
            elif tk_use == 'register':
                self.register_key(user, publicKey)
            self.db.set_user(user_id, {'lastAuthedMsg': time.time()})
            print('authed')
            return jsonify({'authSuccess': True})

    def is_authenticated(self, user_id: int) -> bool:
        # Su ultimo mensaje autenticado fue hace menos de 5 min
        user = self.db.get_user(user_id)
        if user == None or user.get('lastAuthedMsg') == None: return False
        is_authed = 300 >= time.time() - user['lastAuthedMsg']
        if is_authed : self.db.set_user(user_id, {'lastAuthedMsg': time.time()})
        return is_authed
    
    def gen_temp_link(self, user_id: int, name: str, tk_use: str = 'auto') -> str:
        if tk_use == 'auto':
            tk_use = 'login' if self.is_registered(user_id) else 'register'
        baseUrl = "https://ruminini.github.io/Auth-Test/"
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        self.db.set_user(user_id,{'token': token,'tk_time': time.time(), 'tk_use': tk_use, 'name': name})
        print(user_id,{'token': token,'tk_time': time.time(), 'tk_use': tk_use, 'name': name})
        return f"{baseUrl}/?token={token}&id={user_id}"
    
    def gen_challenge(self):
        return list(bytearray(os.urandom(32)))

    def is_registered(self, user_id: int) -> bool:
        user = self.db.get_user(user_id)
        return user != None and len(user.get('publicKeys', [])) > 0

    def validate_key(self, user: dict, publicKey: str) -> bool:
        publicKeys = user.get('publicKeys', [])
        print(publicKeys)
        print(publicKey)
        print(publicKey in publicKeys)
        return publicKey in publicKeys
    
    def validate_token(self, user: dict, token: str) -> bool:
        lastToken = user['token']
        creationTime = user['tk_time']
        return lastToken == token and time.time() - creationTime < 300

    def register_key(self, user: dict, publicKey: str) -> None:
        publicKeys = user.get('publicKeys', [])
        publicKeys.append(publicKey)
        self.db.set_user(user['_id'], {'publicKeys': publicKeys})

    def reset_account(self, telegramId: int) -> None:
        # TODO Delete the user data from the database
        return True

    def get_credential_options(self, tk_use, user):
        if tk_use == 'register':
            return {
                'publicKey': {
                    'challenge': self.gen_challenge(),
                    'rp': {
                        'name': 'WeatherWiz',
                        'id': 'ruminini.github.io'
                    },
                    'user': {
                        'id': list((user['_id']).to_bytes(16, 'big')),
                        'name': user['name'],
                        'displayName': user['name']
                    },
                    'pubKeyCredParams': [
                        {'type': "public-key", 'alg': -7},
                        {'type': "public-key", 'alg': -257}
                    ],
                    'authenticatorSelection': {
                        'authenticatorAttachment': "platform",
                        'residentKey': "required",
                        'requireResidentKey': True,
                        'userVerification': "required"
                    },
                    'timeout': 60000,
                    'attestation': "direct",
                    'extensions': {
                        'credProps': True
                    }
                }}
        return {
            'publicKey': {
                'challenge': self.gen_challenge(),
                'timeout': 60000,
                'rpId': "ruminini.github.io",
                'userVerification': "required"
            }}