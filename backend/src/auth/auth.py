import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
# from urllib.request import urlopen
#https://{{YOUR_DOMAIN}}/authorize?audience={{API_IDENTIFIER}}&response_type=tok
#https://marswatkins.auth0.com/authorize?audience=coffeeshop&response_type=token&client_id=aa92SyG0m62pbWpOCnzHBxDbM6nnl9My&redirect_uri=http://localhost:5432/login-results
#manager: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5qWXlNRVUwTUVRME4wVTVPVEl4TjBVMlF6azNORGN5TWpsRE1UUkROalpFTWpNeU9ERXdNUSJ9.eyJpc3MiOiJodHRwczovL21hcnN3YXRraW5zLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTg0ZjViMGFkMzQ1OTBiZTFkZGNjZDYiLCJhdWQiOiJjb2ZmZWVzaG9wIiwiaWF0IjoxNTg1NzczNDIyLCJleHAiOjE1ODU3ODA2MjIsImF6cCI6ImFhOTJTeUcwbTYycGJXcE9DbnpIQnhEYk02bm5sOU15Iiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6ZHJpbmtzIiwiZ2V0OmRyaW5rcy1kZXRhaWwiLCJwYXRjaDpkcmlua3MiLCJwb3N0OmRyaW5rcyJdfQ.KbLXkyOzhOc4L-YmpbncIIsS5PAd-qMiGIQJFuhQu9DNNy3O6kRQXgZHvjZpgRIHp_mrxBga5OCJYUkLCvhVJUMEFLe251D-3ZLWY8IzTzbBHOlWxO1VjMzgRYRCxaBn27pUuRLu5LMnx9zOa4YaGYRjsBTO3qH7Bl-bSiIY3KRGv9qgfr981-bKd4Fo-RsaEyKDRRdWusK3CugTFKvcMbn9XJfCZxCioP4cGiG20CYXu28I2XIZdgCOz10wDmxhtg-dD5ml4RGJCkXkwHEjVSMQJyEMd5ezDGueBxeIVHVkR3lV9Wdi8AV6RoTt2aaZFZV98I-dZ4G1fpC4NO2hKw
#barista: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5qWXlNRVUwTUVRME4wVTVPVEl4TjBVMlF6azNORGN5TWpsRE1UUkROalpFTWpNeU9ERXdNUSJ9.eyJpc3MiOiJodHRwczovL21hcnN3YXRraW5zLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTg0ZmFmM2FiODhkNDBiZThhMmU2N2QiLCJhdWQiOiJjb2ZmZWVzaG9wIiwiaWF0IjoxNTg1ODQyMTgzLCJleHAiOjE1ODU4NDkzODMsImF6cCI6ImFhOTJTeUcwbTYycGJXcE9DbnpIQnhEYk02bm5sOU15Iiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6ZHJpbmtzLWRldGFpbCJdfQ.ehEacdKLzqYat8HQ5tdgu5fJZFL98bmn0BI-iRq8STqjfWcRQbvh41w438GPAn4AKKfF4q5R1_OR4LFqdI9_0rWQiejsTao84twQnXhgqF6vh_Fte82mw6AtShQW_5kZejtKKBR5PYSc_3nD5DHDVDpJco52P8CB2X4DKnbB168SQS_RcvwosaUhVeHCW2mWyCJhFwa-qDowjM0jhurTcKcIMLxlVLtrx8b00tyVclm5YkPyKVOgNXKDzTeDxNDXxFp2Y0pSW4OEBPAzQ7LLaD0fZr8vzu5irv_1Q71mmNyw3J2zJSuMIF3sYea9-26ZoAzbJos8OsKqdzB3jz0m9w

AUTH0_DOMAIN = 'marswatkins.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffeeshop'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header
def get_token_auth_header():

    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorized header is expected.'
    }, 401)

    parts = auth.split()
    if part[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorized header must start with "bearer"'
    }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'No token was found'
    }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorized header must be bearer token'
    }, 401)

    token = parts[1]
    return token
# implement get_token_auth_header() method
# it should attempt to get the header from the request
# it should raise an AuthError if no header is present
# it should attempt to split bearer and the token
# it should raise an AuthError if the header is malformed return the token part of the header

def check_permissions(permission, payload):
    permissions = payload.get('permissions')
    if not permissions or permission not in permissions:
        raise AuthError('unauthorized', 403)
    return True
# implement check_permissions(permission, payload) method
# @INPUTS
# permission: string permission (i.e. 'post:drink')
# payload: decoded jwt payload
# it should raise an AuthError if permissions are not included in the payload
# !!NOTE check your RBAC settings in Auth0
# it should raise an AuthError if the requested permission string is not in the payload permissions array return true otherwise

def verify_decode_jwt(token):
    jsonurl = urlopen('https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwts = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorized malformed.'
    }, 401)

    for key in jwts['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            payload = jwt.decode(token, rsa_key, algorithms=ALGORITHMS, audience=API_AUDIENCE, issuer='https://' + AUTH0_DOMAIN + '/')

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token Expired'
        }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please check the audience and issuer'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key'
    }, 400)

# implement verify_decode_jwt(token) method
# @INPUTS
# token: a json web token (string)
# it should be an Auth0 token with key id (kid)
# it should verify the token using Auth0 /.well-known/jwks.json
# it should decode the payload from the token
# it should validate the claims
# return the decoded payload
# !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()
            except:
                abort(401)
            try:
                payload = verify_decode_jwt(token)
            except:
                abort(401)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
# implement @requires_auth(permission) decorator method
# @INPUTS
# permission: string permission (i.e. 'post:drink')

# it should use the get_token_auth_header method to get the token
# it should use the verify_decode_jwt method to decode the jwt
# it should use the check_permissions method validate claims and check the requested permission
# return the decorator which passes the decoded payload to the decorated method

