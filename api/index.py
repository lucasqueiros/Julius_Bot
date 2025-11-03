from flask import Flask, request

app = Flask(__name__)

# rota q servirá de webhook
@app.route('/', methods=['POST'])
def handle_webhook():
    print("Webhook recebido!")
    print(request.json)     # Apenas para ver os dados do Telegram nos logs
    return "Webhook recebido", 200

# Rota get inicial
@app.route('/', methods=['GET'])
def health_check():
    return "Estou vivo!", 200