from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError

from db import get_courses_collection
from backend.course import CourseStatus, serialize


class ServiceError(Exception):
    def __init__(self, status, message, code=None):
        self.status = status
        self.message = message
        self.code = code
        super().__init__(message)


REQUIRED_FIELDS = ("codigo", "nome", "instrutor")


def create_course(payload, admin_email):
    if not isinstance(payload, dict):
        raise ServiceError(400, "Body invalido", "INVALID_BODY")

    for field in REQUIRED_FIELDS:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ServiceError(400, f"Campo '{field}' obrigatorio", "MISSING_FIELD")

    doc = {
        "codigo": payload["codigo"].strip(),
        "nome": payload["nome"].strip(),
        "instrutor": payload["instrutor"].strip(),
        "data_cadastro": datetime.utcnow(),
        "status": CourseStatus.DISPONIVEL.value,
        "admin_email": admin_email,
    }

    try:
        result = get_courses_collection().insert_one(doc)
    except DuplicateKeyError:
        raise ServiceError(409, "Codigo de curso ja existe", "CODIGO_DUPLICADO")

    doc["_id"] = result.inserted_id
    return serialize(doc)


def list_courses(status_filter):
    valid_values = {s.value for s in CourseStatus}
    query = {}

    if status_filter is None:
        query["status"] = CourseStatus.DISPONIVEL.value
    elif status_filter.lower() == "all":
        pass
    elif status_filter in valid_values:
        query["status"] = status_filter
    else:
        raise ServiceError(400, "Status invalido", "INVALID_STATUS")

    cursor = get_courses_collection().find(query).sort("data_cadastro", -1)
    return [serialize(d) for d in cursor]


def cancel_course(course_id):
    try:
        oid = ObjectId(course_id)
    except (InvalidId, TypeError):
        raise ServiceError(400, "ID invalido", "INVALID_ID")

    result = get_courses_collection().update_one(
        {"_id": oid},
        {"$set": {"status": CourseStatus.CANCELADO.value}},
    )

    if result.matched_count == 0:
        raise ServiceError(404, "Curso nao encontrado", "NOT_FOUND")
