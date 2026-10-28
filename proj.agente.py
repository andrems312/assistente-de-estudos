#python
from openai import OpenAI
from datetime import datetime


# ==========================================
# API KEY
# ==========================================

api_key = input("Cole sua API Key da OpenRouter: ")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)


# ==========================================
# FERRAMENTA: HORA ATUAL
# ==========================================

def obter_hora_atual():
    agora = datetime.now()
    return agora.strftime("%H:%M")


# ==========================================
# FERRAMENTA: DATA ATUAL
# ==========================================

def obter_data_atual():
    agora = datetime.now()
    return agora.strftime("%d/%m/%Y")


# ==========================================
# FERRAMENTAS DISPONÍVEIS PARA A IA
# ==========================================

ferramentas = [
    {
        "type": "function",
        "function": {
            "name": "obter_hora_atual",
            "description": "Retorna a hora atual.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obter_data_atual",
            "description": "Retorna a data atual.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


# ==========================================
# HISTÓRICO DA CONVERSA
# ==========================================

mensagens = [
    {
        "role": "system",
        "content": """
Você é um assistente de estudos.

Ajude o usuário com perguntas de programação,
tecnologia e outros assuntos.

Responda de forma simples e fácil de entender.

Quando o usuário perguntar a data atual,
utilize a ferramenta obter_data_atual.

Quando o usuário perguntar a hora atual,
utilize a ferramenta obter_hora_atual.
"""
    }
]


# ==========================================
# INÍCIO
# ==========================================

print("\n================================")
print("   ASSISTENTE DE ESTUDOS")
print("================================")
print("Assistente pronto!")
print("Digite 'sair' para encerrar.")


# ==========================================
# LOOP PRINCIPAL
# ==========================================

while True:

    pergunta = input("\nVocê: ")

    if pergunta.lower() == "sair":
        print("Até mais!")
        break

    mensagens.append({
        "role": "user",
        "content": pergunta
    })


    # ==========================================
    # PRIMEIRA CHAMADA PARA A IA
    # ==========================================

    resposta = client.chat.completions.create(
        model="openrouter/free",
        messages=mensagens,
        tools=ferramentas
    )

    mensagem = resposta.choices[0].message


    # ==========================================
    # IA PEDIU UMA FERRAMENTA
    # ==========================================

    if mensagem.tool_calls:

        chamada = mensagem.tool_calls[0]

        if chamada.function.name == "obter_hora_atual":

            resultado = obter_hora_atual()

        elif chamada.function.name == "obter_data_atual":

            resultado = obter_data_atual()

        else:

            resultado = "Ferramenta desconhecida."


        # Guarda a solicitação da ferramenta
        mensagens.append({
            "role": "assistant",
            "content": mensagem.content,
            "tool_calls": [
                {
                    "id": chamada.id,
                    "type": "function",
                    "function": {
                        "name": chamada.function.name,
                        "arguments": chamada.function.arguments
                    }
                }
            ]
        })


        # Guarda o resultado da ferramenta
        mensagens.append({
            "role": "tool",
            "tool_call_id": chamada.id,
            "content": resultado
        })


        # ==========================================
        # SEGUNDA CHAMADA PARA A IA
        # ==========================================

        resposta_final = client.chat.completions.create(
            model="openrouter/free",
            messages=mensagens,
            tools=ferramentas
        )

        texto_final = resposta_final.choices[0].message.content

        mensagens.append({
            "role": "assistant",
            "content": texto_final
        })

        print("\nAssistente:", texto_final)


    # ==========================================
    # RESPOSTA NORMAL
    # ==========================================

    else:

        texto_resposta = mensagem.content

        mensagens.append({
            "role": "assistant",
            "content": texto_resposta
        })

        print("\nAssistente:", texto_resposta)