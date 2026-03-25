from flask import Flask, request, jsonify
from datetime import datetime
import requests
import uuid
from db import MongoService


app = Flask(__name__)
db_service = MongoService()


API_USUARIOS_URL = "http://18.228.48.67/users/"


@app.route('/pagamento', methods=['GET'])
def get_pagamentos():
    cliente_id = request.args.get('cliente_id')
    pagamentos = db_service.listar_pagamentos(cliente_id)
    return jsonify(pagamentos), 200

@app.route('/pagamento/<string:id>', methods=['DELETE'])
def delete_pagamento(id):
    deletado = db_service.deletar_pagamento(id)
    if not deletado:
        return {}, 404
    return {}, 200

@app.route('/pagamento', methods=['POST'])
def create_pagamento():
    data = request.get_json()
    campos_obrigatorios = ['cliente_id', 'codigo', 'valor_total', 'tipo', 'parcelas']
    for campo in campos_obrigatorios:
        if not data or campo not in data:
            return {}, 400
    if data['tipo'] not in ['PIX', 'Crédito']:
        return {}, 400
    cliente_id = data['cliente_id']
    try:
        response = requests.get(f"{API_USUARIOS_URL}{cliente_id}", timeout=5)
        if response.status_code not in [200, 201]:
            return {}, 404
        usuario = response.json()
    except requests.exceptions.RequestException:
        return {}, 500
    valor_total = float(data['valor_total'])
    parcelas = int(data['parcelas'])
    valor_parcela = round(valor_total / parcelas, 2) #round para evitar bo com float 
    novo_pagamento = {
        "ID": str(uuid.uuid4()),
        "cliente_id": cliente_id,
        "cliente_email": usuario.get("email", ""),
        "codigo": data['codigo'],
        "valor_total": valor_total,
        "tipo": data['tipo'],
        "parcelas": parcelas,
        "valor_parcela": valor_parcela,
        "data": datetime.now().isoformat()
    }
    db_service.salvar_pagamento(novo_pagamento)
    novo_pagamento.pop("_id", None)
    return jsonify(novo_pagamento), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
