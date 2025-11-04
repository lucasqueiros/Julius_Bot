"""
API Webhook para Telegram Bot - Vercel Serverless
Recebe e processa atualizações do Telegram via webhook
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

# Adicionar diretório raiz ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update
from telegram.ext import Application, ContextTypes
from bot.telegram_bot import FinanceBot


# Inicializar o bot globalmente (cache entre invocações)
_bot_instance = None


def get_bot():
    """Obtém instância do bot (singleton para melhor performance)"""
    global _bot_instance
    
    if _bot_instance is None:
        # Carregar variáveis de ambiente
        TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        
        if not all([TELEGRAM_TOKEN, GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
            raise ValueError("Variáveis de ambiente faltando")
        
        _bot_instance = FinanceBot(
            token=TELEGRAM_TOKEN,
            gemini_key=GEMINI_API_KEY,
            supabase_url=SUPABASE_URL,
            supabase_key=SUPABASE_KEY
        )
    
    return _bot_instance


class handler(BaseHTTPRequestHandler):
    """Handler serverless da Vercel"""
    
    def do_POST(self):
        """Processa requisições POST do Telegram webhook"""
        try:
            # Ler corpo da requisição
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Parse do JSON
            update_data = json.loads(body.decode('utf-8'))
            
            # Criar objeto Update do python-telegram-bot
            update = Update.de_json(update_data, get_bot().app.bot)
            
            # Processar update de forma assíncrona
            import asyncio
            asyncio.run(process_update(update))
            
            # Responder ao Telegram
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
            
        except Exception as e:
            print(f"Erro ao processar webhook: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
    
    def do_GET(self):
        """Health check endpoint"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "ok",
            "message": "Telegram Bot Webhook is running",
            "bot_name": "Julius Finance Bot"
        }
        
        self.wfile.write(json.dumps(response).encode())


async def process_update(update: Update):
    """
    Processa uma atualização do Telegram
    
    Args:
        update: Objeto Update do Telegram
    """
    try:
        bot = get_bot()
        
        # Processar a atualização através da aplicação
        await bot.app.process_update(update)
        
    except Exception as e:
        print(f"Erro ao processar update: {e}")
        raise
