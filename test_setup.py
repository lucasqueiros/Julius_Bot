#!/usr/bin/env python3
"""
Script de testes locais para verificar se tudo está funcionando
Execute antes de fazer deploy
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def verificar_variaveis_ambiente():
    """Verifica se todas as variáveis de ambiente necessárias estão configuradas"""
    
    print("\n" + "=" * 70)
    print("🔍 VERIFICANDO VARIÁVEIS DE AMBIENTE")
    print("=" * 70 + "\n")
    
    variaveis = {
        "TELEGRAM_BOT_TOKEN": "Token do Bot do Telegram",
        "GEMINI_API_KEY": "Chave da API do Gemini",
        "SUPABASE_URL": "URL do projeto Supabase",
        "SUPABASE_KEY": "Service Role Key do Supabase"
    }
    
    todas_ok = True
    
    for var, descricao in variaveis.items():
        valor = os.getenv(var)
        if valor:
            # Mostrar apenas primeiros 10 caracteres por segurança
            valor_masked = valor[:10] + "..." if len(valor) > 10 else valor
            print(f"✅ {var:<25} = {valor_masked}")
        else:
            print(f"❌ {var:<25} = NÃO CONFIGURADA")
            todas_ok = False
    
    print("\n" + "=" * 70)
    
    if todas_ok:
        print("✅ Todas as variáveis de ambiente estão configuradas!\n")
    else:
        print("❌ Algumas variáveis estão faltando!")
        print("\n💡 Configure-as no arquivo .env\n")
    
    return todas_ok


def testar_imports():
    """Testa se todas as bibliotecas necessárias estão instaladas"""
    
    print("\n" + "=" * 70)
    print("📦 TESTANDO IMPORTS")
    print("=" * 70 + "\n")
    
    imports_necessarios = [
        ("telegram", "python-telegram-bot"),
        ("google.generativeai", "google-generativeai"),
        ("supabase", "supabase"),
        ("httpx", "httpx"),
        ("dotenv", "python-dotenv"),
    ]
    
    todos_ok = True
    
    for modulo, pacote in imports_necessarios:
        try:
            __import__(modulo)
            print(f"✅ {pacote:<30} OK")
        except ImportError:
            print(f"❌ {pacote:<30} NÃO INSTALADO")
            todos_ok = False
    
    print("\n" + "=" * 70)
    
    if todos_ok:
        print("✅ Todas as bibliotecas estão instaladas!\n")
    else:
        print("❌ Algumas bibliotecas estão faltando!")
        print("\n💡 Execute: pip install -r requirements.txt\n")
    
    return todos_ok


def testar_conexao_gemini():
    """Testa conexão com a API do Gemini"""
    
    print("\n" + "=" * 70)
    print("🤖 TESTANDO GEMINI AI")
    print("=" * 70 + "\n")
    
    try:
        from bot.gemini_classifier import GeminiClassifier
        
        print("⏳ Inicializando classificador...")
        classificador = GeminiClassifier()
        
        print("⏳ Testando classificação...")
        resultado = classificador.classificar("Gastei 50 no almoço")
        
        if resultado:
            print(f"✅ Gemini funcionando!")
            print(f"\n   Teste: 'Gastei 50 no almoço'")
            print(f"   Tipo: {resultado['tipo']}")
            print(f"   Valor: R$ {resultado['valor']:.2f}")
            print(f"   Categoria: {resultado['categoria']}")
            print(f"   Confiança: {resultado['confianca']:.0%}")
            print("\n" + "=" * 70)
            return True
        else:
            print("❌ Falha na classificação")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar Gemini: {e}")
        print("\n💡 Verifique se a GEMINI_API_KEY está correta")
        return False


def testar_conexao_supabase():
    """Testa conexão com o Supabase"""
    
    print("\n" + "=" * 70)
    print("🗄️  TESTANDO SUPABASE")
    print("=" * 70 + "\n")
    
    try:
        from database.supabase_client import SupabaseClient
        
        print("⏳ Conectando ao Supabase...")
        db = SupabaseClient()
        
        print("⏳ Testando leitura...")
        transacoes = db.buscar_ultimas_transacoes(1)
        
        print(f"✅ Supabase conectado!")
        print(f"\n   Total de transações na última consulta: {len(transacoes)}")
        print("\n" + "=" * 70)
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar Supabase: {e}")
        print("\n💡 Verifique SUPABASE_URL e SUPABASE_KEY")
        print("💡 Certifique-se que a tabela 'transacoes' existe")
        return False


def testar_bot_telegram():
    """Testa inicialização do bot do Telegram"""
    
    print("\n" + "=" * 70)
    print("📱 TESTANDO BOT DO TELEGRAM")
    print("=" * 70 + "\n")
    
    try:
        from bot.telegram_bot import FinanceBot
        
        TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        
        print("⏳ Inicializando bot...")
        bot = FinanceBot(
            token=TELEGRAM_TOKEN,
            gemini_key=GEMINI_API_KEY,
            supabase_url=SUPABASE_URL,
            supabase_key=SUPABASE_KEY
        )
        
        print(f"✅ Bot inicializado com sucesso!")
        print(f"\n   Bot está pronto para uso!")
        print("\n" + "=" * 70)
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar bot: {e}")
        print("\n💡 Verifique se TELEGRAM_BOT_TOKEN está correto")
        return False


def main():
    """Função principal"""
    
    print("\n" + "=" * 70)
    print("🧪 TESTE DE CONFIGURAÇÃO - JULIUS FINANCE BOT")
    print("=" * 70)
    
    resultados = []
    
    # 1. Verificar variáveis de ambiente
    resultados.append(("Variáveis de Ambiente", verificar_variaveis_ambiente()))
    
    # 2. Testar imports
    resultados.append(("Imports", testar_imports()))
    
    # Se os básicos passaram, testar conexões
    if resultados[0][1] and resultados[1][1]:
        # 3. Testar Gemini
        resultados.append(("Gemini AI", testar_conexao_gemini()))
        
        # 4. Testar Supabase
        resultados.append(("Supabase", testar_conexao_supabase()))
        
        # 5. Testar Bot
        resultados.append(("Bot Telegram", testar_bot_telegram()))
    
    # Resumo final
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES")
    print("=" * 70 + "\n")
    
    for nome, passou in resultados:
        status = "✅ OK" if passou else "❌ FALHOU"
        print(f"{nome:<25} {status}")
    
    total = len(resultados)
    passou_todos = sum(1 for _, p in resultados if p)
    
    print("\n" + "=" * 70)
    print(f"Testes passados: {passou_todos}/{total}")
    print("=" * 70 + "\n")
    
    if passou_todos == total:
        print("🎉 TUDO PRONTO PARA DEPLOY!\n")
        print("📋 Próximos passos:")
        print("   1. Fazer commit: git add . && git commit -m 'Pronto para Vercel'")
        print("   2. Push: git push origin main")
        print("   3. Deploy na Vercel: vercel --prod")
        print("   4. Configurar webhook: python setup_webhook.py")
        return 0
    else:
        print("⚠️  CORRIJA OS ERROS ANTES DE FAZER DEPLOY!\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
