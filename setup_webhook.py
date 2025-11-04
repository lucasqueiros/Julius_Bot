#!/usr/bin/env python3
"""
Script para configurar webhook do Telegram Bot
Execute este script após fazer deploy na Vercel
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


def configurar_webhook(webhook_url: str, token: str):
    """
    Configura o webhook do Telegram Bot
    
    Args:
        webhook_url: URL do webhook (ex: https://seu-app.vercel.app/api/webhook)
        token: Token do bot do Telegram
    """
    
    # Endpoint da API do Telegram
    api_url = f"https://api.telegram.org/bot{token}/setWebhook"
    
    # Parâmetros
    params = {
        "url": webhook_url,
        "max_connections": 100,
        "drop_pending_updates": True  # Limpar atualizações antigas
    }
    
    print("=" * 70)
    print("🔧 CONFIGURANDO WEBHOOK DO TELEGRAM")
    print("=" * 70 + "\n")
    print(f"📍 URL do webhook: {webhook_url}")
    print(f"🤖 Bot token: {token[:10]}...")
    print("\n⏳ Enviando requisição para o Telegram...\n")
    
    try:
        # Fazer requisição
        response = requests.post(api_url, json=params)
        result = response.json()
        
        if result.get("ok"):
            print("✅ Webhook configurado com sucesso!")
            print(f"\n📋 Detalhes:")
            print(f"   URL: {webhook_url}")
            print(f"   Status: Ativo")
            print(f"\n💡 Teste enviando uma mensagem para o bot!")
            return True
        else:
            print("❌ Erro ao configurar webhook!")
            print(f"\n📋 Detalhes do erro:")
            print(f"   Código: {result.get('error_code')}")
            print(f"   Descrição: {result.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False


def verificar_webhook(token: str):
    """
    Verifica o status atual do webhook
    
    Args:
        token: Token do bot do Telegram
    """
    
    api_url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
    
    print("\n" + "=" * 70)
    print("🔍 VERIFICANDO STATUS DO WEBHOOK")
    print("=" * 70 + "\n")
    
    try:
        response = requests.get(api_url)
        result = response.json()
        
        if result.get("ok"):
            info = result.get("result", {})
            
            print("📊 Status atual:")
            print(f"   URL: {info.get('url', 'Não configurado')}")
            print(f"   Atualizações pendentes: {info.get('pending_update_count', 0)}")
            print(f"   Última chamada: {info.get('last_error_date', 'Nunca')}")
            
            if info.get('last_error_message'):
                print(f"   ⚠️ Último erro: {info.get('last_error_message')}")
            else:
                print(f"   ✅ Sem erros recentes")
                
            return True
        else:
            print("❌ Erro ao verificar webhook")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False


def remover_webhook(token: str):
    """
    Remove o webhook (volta para polling)
    
    Args:
        token: Token do bot do Telegram
    """
    
    api_url = f"https://api.telegram.org/bot{token}/deleteWebhook"
    
    print("\n" + "=" * 70)
    print("🗑️  REMOVENDO WEBHOOK")
    print("=" * 70 + "\n")
    
    try:
        response = requests.post(api_url, json={"drop_pending_updates": True})
        result = response.json()
        
        if result.get("ok"):
            print("✅ Webhook removido com sucesso!")
            print("\n💡 O bot agora pode usar polling (run_polling)")
            return True
        else:
            print("❌ Erro ao remover webhook")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False


def main():
    """Função principal"""
    
    print("\n" + "=" * 70)
    print("🤖 CONFIGURADOR DE WEBHOOK - TELEGRAM BOT")
    print("=" * 70 + "\n")
    
    # Obter token
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("❌ Erro: TELEGRAM_BOT_TOKEN não encontrado!")
        print("\n💡 Configure no arquivo .env:")
        print("   TELEGRAM_BOT_TOKEN=seu_token_aqui")
        return
    
    # Menu de opções
    print("Escolha uma opção:\n")
    print("1. Configurar webhook (para Vercel)")
    print("2. Verificar status do webhook")
    print("3. Remover webhook (voltar para polling)")
    print("4. Sair")
    
    escolha = input("\n👉 Digite o número da opção: ").strip()
    
    if escolha == "1":
        print("\n📝 Informe a URL do seu webhook na Vercel")
        print("   Exemplo: https://seu-app.vercel.app/api/webhook")
        webhook_url = input("\n👉 URL: ").strip()
        
        if not webhook_url:
            print("❌ URL não pode estar vazia!")
            return
        
        configurar_webhook(webhook_url, token)
        verificar_webhook(token)
        
    elif escolha == "2":
        verificar_webhook(token)
        
    elif escolha == "3":
        confirmar = input("\n⚠️  Tem certeza que deseja remover o webhook? (s/n): ").lower()
        if confirmar == 's':
            remover_webhook(token)
        else:
            print("❌ Operação cancelada")
            
    elif escolha == "4":
        print("\n👋 Até logo!")
        
    else:
        print("\n❌ Opção inválida!")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
