import json
from functools import wraps
from urllib.request import urlopen

import jwt
from flask import current_app, g, jsonify, request

from app import cache


class CognitoTokenValidator:
    def __init__(self, region: str, user_pool_id: str, client_id: str):
        self.region = region
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.issuer = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}"
        self.jwks_url = f"{self.issuer}/.well-known/jwks.json"

    def get_jwks(self) -> dict:
        cache_key = "cognito:jwks"

        cached_jwks = cache.get(cache_key)
        if cached_jwks is not None:
            current_app.logger.info("Using cached Cognito JWKS.")
            return cached_jwks

        current_app.logger.info("Fetching Cognito JWKS from AWS.")
        with urlopen(self.jwks_url) as response:
            jwks = json.loads(response.read())

        cache.set(cache_key, jwks)
        return jwks

    def validate_token(self, token: str) -> dict:
        jwks = self.get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        key = None
        for jwk in jwks.get("keys", []):
            if jwk.get("kid") == kid:
                key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
                break

        if key is None:
            raise jwt.InvalidTokenError("Unable to find matching JWKS key.")

        claims = jwt.decode(
            token,
            key=key,
            algorithms=["RS256"],
            issuer=self.issuer,
            audience=self.client_id,
        )

        return claims


def _build_validator() -> CognitoTokenValidator:
    region = current_app.config.get("COGNITO_REGION")
    user_pool_id = current_app.config.get("COGNITO_USER_POOL_ID")
    client_id = current_app.config.get("COGNITO_APP_CLIENT_ID")

    if not region or not user_pool_id or not client_id:
        raise RuntimeError("Cognito configuration is missing.")

    return CognitoTokenValidator(
        region=region,
        user_pool_id=user_pool_id,
        client_id=client_id,
    )


def require_auth(route_func):
    @wraps(route_func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({
                "error": "Forbidden",
                "detail": "Missing or invalid Authorization header.",
            }), 403

        token = auth_header.removeprefix("Bearer ").strip()

        try:
            validator = _build_validator()
            claims = validator.validate_token(token)

            g.auth_claims = claims
            g.current_user = (
                claims.get("cognito:username")
                or claims.get("username")
                or claims.get("sub")
            )

        except jwt.ExpiredSignatureError:
            return jsonify({
                "error": "Forbidden",
                "detail": "Token has expired.",
            }), 403
        except jwt.InvalidTokenError as error:
            return jsonify({
                "error": "Forbidden",
                "detail": f"Invalid token: {str(error)}",
            }), 403
        except Exception as error:
            return jsonify({
                "error": "Forbidden",
                "detail": f"Authentication failed: {str(error)}",
            }), 403

        return route_func(*args, **kwargs)

    return wrapper