import os
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "dev-fa0at04h4b7wjopr.us.auth0.com")
AUTH0_AUDIENCE = os.environ.get(
    "AUTH0_AUDIENCE", "https://dev-fa0at04h4b7wjopr.us.auth0.com/api/v2/"
)
AUTH0_ISSUER = f"https://{AUTH0_DOMAIN}/"
JWKS_URL = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
ROLES_CLAIM = os.environ.get("AUTH0_ROLES_CLAIM", "https://prova/roles")

_jwks_client = jwt.PyJWKClient(JWKS_URL)


def _unauthorized(message):
    return jsonify({"error": "unauthorized", "message": message}), 401


def _forbidden(message):
    return jsonify({"error": "forbidden", "message": message}), 403


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_app.config.get("AUTH_DISABLED"):
            g.user = {"email": "dev@local", ROLES_CLAIM: ["ADMIN", "USER"]}
            return f(*args, **kwargs)

        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return _unauthorized("missing or malformed Authorization header")

        token = parts[1]
        try:
            signing_key = _jwks_client.get_signing_key_from_jwt(token).key
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=AUTH0_AUDIENCE,
                issuer=AUTH0_ISSUER,
            )
        except jwt.PyJWTError as e:
            return _unauthorized(str(e))

        g.user = payload
        return f(*args, **kwargs)

    return decorated


def requires_role(role):
    def decorator(f):
        @wraps(f)
        @requires_auth
        def wrapper(*args, **kwargs):
            roles = g.user.get(ROLES_CLAIM, []) or []
            if role not in roles:
                return _forbidden(f"requires role {role}")
            return f(*args, **kwargs)

        return wrapper

    return decorator
