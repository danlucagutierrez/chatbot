from flask import Flask, request, jsonify
from os import urandom

app = Flask(__name__)

# Define a function to add CORS headers to responses
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5500'  # Allow requests from this origin
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'  # Allow Content-Type header
    response.headers['Access-Control-Allow-Methods'] = 'POST'  # Allow POST requests
    return response

# Register the CORS headers function as a after_request handler
app.after_request(add_cors_headers)


@app.route('/api/validateLink/', methods=['POST'])
def validate_url():
    data = request.json
    # TODO Checkear en db que sea valido
    info = getInfo(data)
    if not info['isValid']:
        return jsonify({'isValid': False})
    return jsonify({
    'isValid': True,
    'createNewCredential': info['create'],
    'credentialOptions': getCredentialOptions(info)})

@app.route('/api/authenticateKey/', methods=['POST'])
def authenticate_key():
    data = request.json
    # TODO verificar que coincida el token
    return jsonify({'authSuccess': True})

def genChallenge():
    return list(bytearray(urandom(32)))

def getInfo(data):
    # TODO obtener de la db toda su info con data[token] y data[id]
    return {
        'isValid': True,
        'create': False,
        'userId': list(bytearray([0] * 16)),
        'name': "user@mail.com",
        'displayName': "user"
    }

def getCredentialOptions(info):
    if info['create']:
        return {
        'publicKey': {
            'challenge': genChallenge(),
            'rp': { 'name': 'WeatherWiz' },
            'user': { 'id': info['userId'], 'name': info['name'], 'displayName': info['displayName'] },
            'pubKeyCredParams': [
                { 'type': "public-key", 'alg': -7 },
                { 'type': "public-key", 'alg': -257 }
            ],
            'authenticatorSelection': { 'authenticatorAttachment': "platform" },
            'timeout': 60000,
            'attestation': "direct"
        }}
    return {
    'publicKey': {
        'challenge': genChallenge(),
        'timeout': 60000,
    }}

if __name__ == '__main__':
    app.run(debug=True)
    
