"""
Aplicação Flask simples inspirada no Reclame Aqui.
Permite o envio e a visualização de reclamações,
armazenadas localmente em um arquivo JSON.
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
from datetime import datetime
from typing import List, Dict, Any

# -----------------------------------------------------------
# Configuração básica
# -----------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "chave-secreta-dev")  # use variável de ambiente em produção
DATA_FILE = "complaints.json"


# -----------------------------------------------------------
# Funções utilitárias
# -----------------------------------------------------------
def load_complaints() -> List[Dict[str, Any]]:
    """Carrega as reclamações do arquivo JSON."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_complaints(complaints: List[Dict[str, Any]]) -> None:
    """Salva a lista completa de reclamações no arquivo JSON."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(complaints, file, ensure_ascii=False, indent=2)


def add_complaint(entry: Dict[str, Any]) -> None:
    """Adiciona uma nova reclamação à base de dados JSON."""
    complaints = load_complaints()
    complaints.append(entry)
    save_complaints(complaints)


# -----------------------------------------------------------
# Rotas
# -----------------------------------------------------------
@app.route("/")
def index():
    """Página inicial — formulário de envio."""
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    """Processa o envio do formulário de reclamação."""
    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip()
    empresa = request.form.get("empresa", "").strip()
    titulo = request.form.get("titulo", "").strip()
    descricao = request.form.get("descricao", "").strip()

    if not nome or not empresa or not titulo or not descricao:
        flash("Por favor, preencha todos os campos obrigatórios.", "error")
        return redirect(url_for("index"))

    entry = {
        "id": int(datetime.utcnow().timestamp() * 1000),
        "nome": nome,
        "email": email,
        "empresa": empresa,
        "titulo": titulo,
        "descricao": descricao,
        "status": "Pendente",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    try:
        add_complaint(entry)
        flash("Reclamação enviada com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao salvar a reclamação: {e}", "error")

    return redirect(url_for("index"))


@app.route("/reclamacoes")
def list_complaints():
    """Lista todas as reclamações cadastradas."""
    complaints = sorted(
        load_complaints(),
        key=lambda c: c.get("created_at", ""),
        reverse=True
    )
    return render_template("complaints.html", complaints=complaints)


@app.route("/reclamacao/<int:complaint_id>")
def complaint_detail(complaint_id: int):
    """Mostra detalhes de uma reclamação específica."""
    for complaint in load_complaints():
        if complaint.get("id") == complaint_id:
            return render_template("detail.html", complaint=complaint)

    flash("Reclamação não encontrada.", "error")
    return redirect(url_for("list_complaints"))


# -----------------------------------------------------------
# Execução
# -----------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
