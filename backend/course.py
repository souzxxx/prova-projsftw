from enum import Enum


class CourseStatus(str, Enum):
    DISPONIVEL = "DISPONIVEL"
    CANCELADO = "CANCELADO"


def serialize(doc):
    return {
        "id": str(doc["_id"]),
        "codigo": doc["codigo"],
        "nome": doc["nome"],
        "instrutor": doc["instrutor"],
        "data_cadastro": doc["data_cadastro"].isoformat() + "Z",
        "status": doc["status"],
        "admin_email": doc["admin_email"],
    }
