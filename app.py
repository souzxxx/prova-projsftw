from flask import Flask, jsonify
from flask_cors import CORS

from backend.courses_routes import bp as courses_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(courses_bp)


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Rota nao encontrada"}), 404


@app.errorhandler(405)
def method_not_allowed(_):
    return jsonify({"error": "Metodo nao permitido"}), 405


@app.errorhandler(500)
def internal_error(_):
    return jsonify({"error": "Erro interno"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
