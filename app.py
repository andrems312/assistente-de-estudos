#python
# ==========================================
# ASSISTENTE DE ESTUDOS - SERVIDOR WEB (Flask)
# ==========================================
# Reaproveita a lógica do agente (OpenRouter + ferramentas)
# e expõe um chat moderno no navegador.
#
# A chave da API fica SOMENTE no servidor (variável de ambiente),
# nunca é enviada para o navegador.
# ==========================================

import os
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, session
from openai import OpenAI

load_dotenv()


# ==========================================
# CONFIGURAÇÃO
# ==========================================

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")

if not API_KEY:
    raise RuntimeError(
        "Defina OPENROUTER_API_KEY. Copie .env.example para .env e cole sua chave."
    )

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)


# ==========================================
# FERRAMENTAS
# ==========================================

# Fuso horário de Brasília (o servidor roda em UTC)
FUSO_BR = ZoneInfo("America/Sao_Paulo")


def obter_hora_atual():
    return datetime.now(FUSO_BR).strftime("%H:%M")


def obter_data_atual():
    return datetime.now(FUSO_BR).strftime("%d/%m/%Y")


FUNCOES = {
    "obter_hora_atual": obter_hora_atual,
    "obter_data_atual": obter_data_atual,
}

ferramentas = [
    {
        "type": "function",
        "function": {
            "name": "obter_hora_atual",
            "description": "Retorna a hora atual.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "obter_data_atual",
            "description": "Retorna a data atual.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Você é um assistente de estudos.\n\n"
        "Ajude o usuário com perguntas de programação, tecnologia e outros assuntos.\n\n"
        "Responda de forma simples e fácil de entender.\n\n"
        "Quando o usuário perguntar a data atual, utilize a ferramenta obter_data_atual.\n"
        "Quando o usuário perguntar a hora atual, utilize a ferramenta obter_hora_atual."
    ),
}


# ==========================================
# HISTÓRICO POR SESSÃO (em memória)
# ==========================================
# Cada navegador recebe um id e tem sua própria conversa.
# Observação: isto fica na memória do processo; ao reiniciar o
# servidor, as conversas são perdidas (suficiente para estudo).

conversas = {}


def obter_historico():
    sid = session.get("sid")
    if not sid or sid not in conversas:
        sid = str(uuid.uuid4())
        session["sid"] = sid
        conversas[sid] = [dict(SYSTEM_PROMPT)]
    return conversas[sid]


# ==========================================
# NÚCLEO DO AGENTE
# ==========================================

def responder(mensagens):
    """Executa uma rodada do agente, tratando chamadas de ferramenta."""

    resposta = client.chat.completions.create(
        model=MODEL,
        messages=mensagens,
        tools=ferramentas,
    )

    mensagem = resposta.choices[0].message

    # A IA pediu ferramentas: executa todas e chama de novo.
    if mensagem.tool_calls:
        mensagens.append({
            "role": "assistant",
            "content": mensagem.content,
            "tool_calls": [
                {
                    "id": c.id,
                    "type": "function",
                    "function": {
                        "name": c.function.name,
                        "arguments": c.function.arguments,
                    },
                }
                for c in mensagem.tool_calls
            ],
        })

        for chamada in mensagem.tool_calls:
            funcao = FUNCOES.get(chamada.function.name)
            resultado = funcao() if funcao else "Ferramenta desconhecida."
            mensagens.append({
                "role": "tool",
                "tool_call_id": chamada.id,
                "content": str(resultado),
            })

        resposta_final = client.chat.completions.create(
            model=MODEL,
            messages=mensagens,
            tools=ferramentas,
        )
        texto = resposta_final.choices[0].message.content
    else:
        texto = mensagem.content

    mensagens.append({"role": "assistant", "content": texto})
    return texto


# ==========================================
# FLASK
# ==========================================

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24).hex())


@app.route("/")
def index():
    return render_template("index.html", model=MODEL)


@app.route("/api/chat", methods=["POST"])
def chat():
    dados = request.get_json(silent=True) or {}
    pergunta = (dados.get("message") or "").strip()

    if not pergunta:
        return jsonify({"error": "Mensagem vazia."}), 400

    mensagens = obter_historico()
    mensagens.append({"role": "user", "content": pergunta})

    try:
        texto = responder(mensagens)
    except Exception as e:
        # Remove a pergunta pendente para não corromper o histórico.
        if mensagens and mensagens[-1].get("role") == "user":
            mensagens.pop()
        return jsonify({"error": f"Erro ao falar com o modelo: {e}"}), 502

    return jsonify({"reply": texto})


@app.route("/api/reset", methods=["POST"])
def reset():
    sid = session.get("sid")
    if sid:
        conversas[sid] = [dict(SYSTEM_PROMPT)]
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
