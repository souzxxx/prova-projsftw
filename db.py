import os
from pymongo import MongoClient


class MongoService:
    def __init__(self):
        mongo_url = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.client = MongoClient(mongo_url)
        self.db = self.client["pagamentos_db"]
        self.collection = self.db["pagamentos"]

    def salvar_pagamento(self, pagamento_data: dict):
        result = self.collection.insert_one(pagamento_data)
        return str(result.inserted_id)

    def listar_pagamentos(self, cliente_id=None):
        filtro = {}
        if cliente_id:
            filtro["cliente_id"] = cliente_id
        pagamentos = list(self.collection.find(filtro))
        for p in pagamentos:
            p["_id"] = str(p["_id"])
        return pagamentos

    def buscar_pagamento(self, pagamento_id: str):
        pagamento = self.collection.find_one({"ID": pagamento_id})
        if pagamento:
            pagamento["_id"] = str(pagamento["_id"])
        return pagamento

    def deletar_pagamento(self, pagamento_id: str):
        result = self.collection.delete_one({"ID": pagamento_id})
        return result.deleted_count > 0
