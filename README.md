# 🤖 Assistente de Estudos

Um chatbot de estudos com interface web moderna, construído em **Python + Flask** e
conectado à **OpenRouter**. O agente responde dúvidas de programação e tecnologia e
possui ferramentas para informar a **hora** e a **data** atuais.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Flask](https://img.shields.io/badge/Flask-3.x-black) ![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Recursos

- Interface de chat moderna (tema escuro, gradientes, animações, responsiva)
- Renderização de Markdown e blocos de código nas respostas
- Ferramentas da IA: hora atual e data atual
- Histórico de conversa por sessão
- **Chave de API protegida no servidor** (nunca exposta no navegador)

## 🚀 Como rodar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure a chave de API:
   ```bash
   # Copie o exemplo e edite o .env com sua chave da OpenRouter
   copy .env.example .env    # Windows
   # cp .env.example .env    # Linux / macOS
   ```
   Pegue sua chave em https://openrouter.ai/keys

3. Inicie o servidor:
   ```bash
   python app.py
   ```

4. Abra no navegador: **http://localhost:5000**

## 🗂️ Estrutura

```
proj agente/
├── app.py              # Servidor Flask + lógica do agente
├── proj.agente.py      # Versão original em linha de comando (CLI)
├── templates/
│   └── index.html      # Página do chat
├── static/
│   ├── style.css       # Estilos
│   └── app.js          # Lógica do front-end
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## ⚙️ Variáveis de ambiente

| Variável             | Descrição                              | Padrão            |
|----------------------|----------------------------------------|-------------------|
| `OPENROUTER_API_KEY` | Sua chave da OpenRouter (obrigatória)  | —                 |
| `OPENROUTER_MODEL`   | Modelo usado                           | `openrouter/free` |
| `FLASK_SECRET_KEY`   | Chave secreta das sessões (opcional)   | gerada automática |

## 📝 Licença

MIT
