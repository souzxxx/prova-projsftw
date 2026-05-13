from flask import Blueprint, request, jsonify, g

from backend.auth import requires_auth, requires_role
from backend import course_service
from backend.course_service import ServiceError

bp = Blueprint("courses", __name__, url_prefix="/courses")


def _error_response(err: ServiceError):
    payload = {"error": err.message}
    if err.code:
        payload["code"] = err.code
    return jsonify(payload), err.status


@bp.post("")
@requires_role("ADMIN")
def create():
    admin_email = g.user.get("email") or g.user.get("https://prova/email") or ""
    try:
        course = course_service.create_course(request.get_json(silent=True), admin_email)
    except ServiceError as e:
        return _error_response(e)
    return jsonify(course), 201


@bp.get("")
@requires_auth
def listar():
    try:
        courses = course_service.list_courses(request.args.get("status"))
    except ServiceError as e:
        return _error_response(e)
    return jsonify(courses), 200


@bp.delete("/<course_id>")
@requires_role("ADMIN")
def cancelar(course_id):
    try:
        course_service.cancel_course(course_id)
    except ServiceError as e:
        return _error_response(e)
    return "", 204
