# AUTENTIZACNI BLUEPRINT pro registraci prihlaseni, refresh, odhlaseni a zmeny
# endpointy maji prefix /api/v1/auth
from __future__ import annotations

from flask import current_app
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt
from marshmallow import Schema, fields, validate
from marshmallow import validates_schema, ValidationError
from marshmallow import fields


from app.extensions import limiter
from app.utils.jwt import get_identity
from app.services.auth_service import (
    register_user,
    authenticate_user,
    refresh_tokens,
    logout_current,
    change_password,
    get_me_payload,
    AuthServiceError,
)
from app.services.audit_events import audit_logout


auth_blp = Blueprint(
    "Auth",
    __name__,
    url_prefix="/api/v1/auth",
    description="Autentizace a správa účtů (JWT access/refresh, RBAC, blacklist)",
)

# SCHEMATA

class RegisterSchema(Schema):
    # Registrace noveho uzivatele
    login = fields.String(
        required=True, validate=validate.Length(min=3, max=80))
    heslo = fields.String(required=True, load_only=True,
                          validate=validate.Length(min=6))
    first_name = fields.String(load_default=None, allow_none=True)
    last_name = fields.String(load_default=None, allow_none=True)
    phone = fields.String(load_default=None, allow_none=True)
    email = fields.Email(load_default=None, allow_none=True)


class LoginSchema(Schema):
    # Prihlaseni, bere login nebo email
    login_nebo_email = fields.String(required=True)
    heslo = fields.String(required=True, load_only=True)


class ChangePasswordSchema(Schema):
    # zmena stareho hesla na nove
    stare_heslo = fields.String(required=True, load_only=True)
    nove_heslo = fields.String(
        required=True, load_only=True, validate=validate.Length(min=6))
    nove_heslo_kontrola = fields.String(required=True, load_only=True)

    @validates_schema
    def validate_match(self, data, **kwargs):
        # shoda nového hesla
        if data["nove_heslo"] != data["nove_heslo_kontrola"]:
            raise ValidationError(
                "Nové heslo a kontrola se neshodují.", field_name="nove_heslo_kontrola")


class MeResponseSchema(Schema):
    # Schema pro /me endpoint (uzivatel)
    login = fields.String(required=True)
    email = fields.Email(allow_none=True)
    phone = fields.String(allow_none=True)
    is_active = fields.Boolean(required=True)
    # Casove znacky formatujeme na HH:MM-DD-MM-YYYY
    created_at = fields.Function(
        lambda obj: obj["created_at"].strftime("%H:%M-%d-%m-%Y") if obj.get("created_at") else None
    )
    updated_at = fields.Function(
        lambda obj: obj["updated_at"].strftime("%H:%M-%d-%m-%Y") if obj.get("updated_at") else None
    )


def _auth_limit():
    # rate limit pro auth endpointy z konfigurace
    return current_app.config.get("RATELIMIT_AUTH", "10 per minute")


# RESOURCES

@auth_blp.route("/register")
class RegisterResource(MethodView):
    @auth_blp.arguments(RegisterSchema)
    @auth_blp.response(201)
    @limiter.limit("5 per minute")
    def post(self, data):
        # Registruje neveho uzivatele (limit 5 pokusu za min)
        try:
            return register_user(
                login=data["login"],
                heslo=data["heslo"],
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                phone=data.get("phone"),
                email=data.get("email"),
            )
        except AuthServiceError as e:
            abort(400, message=str(e))


@auth_blp.route("/login")
class LoginResource(MethodView):
    @auth_blp.arguments(LoginSchema)
    @auth_blp.response(200)
    @limiter.limit(_auth_limit)
    def post(self, data):
        # prihlaseni spolu s tokeny
        try:
            return authenticate_user(
                login_or_email=data["login_nebo_email"],
                heslo=data["heslo"],
            )
        except AuthServiceError as e:
            abort(401, message=str(e))


@auth_blp.route("/refresh")
class RefreshResource(MethodView):
    @jwt_required(refresh=True)
    @auth_blp.response(200)
    @limiter.limit("20 per hour")
    def post(self):
        # obnova tokenu, stary za novy (potrebuje platny refresh token)
        refresh_jwt = get_jwt()
        access, refresh = refresh_tokens(refresh_jwt)
        return {"access_token": access, "refresh_token": refresh}


@auth_blp.route("/logout")
class LogoutResource(MethodView):
    @jwt_required()
    @auth_blp.response(200)
    def post(self):
        # odhlaseni a umisteni tokenu (JTI) do blacklistu
        user_id = get_identity()
        audit_logout(user_id=user_id)
        logout_current()
        return {"message": "Byl jsi odhlášen (token revokován)."}


@auth_blp.route("/change-password")
class ChangePasswordResource(MethodView):
    @jwt_required()
    @auth_blp.arguments(ChangePasswordSchema)
    @auth_blp.response(200)
    def post(self, data):
        # zmena hesla
        user_id = get_identity()
        try:
            msg = change_password(
                user_id=user_id,
                stare_heslo=data["stare_heslo"],
                nove_heslo=data["nove_heslo"],
            )

        except AuthServiceError as e:
            abort(400, message=str(e))
        return {"message": msg}


@auth_blp.route("/me")
class MeResource(MethodView):
    @jwt_required()
    @auth_blp.response(200, MeResponseSchema)
    def get(self):
        # pro vypis dat uzivatele
        user_id = get_identity()
        try:
            return get_me_payload(user_id)
        except AuthServiceError as e:
            abort(404, message=str(e))
