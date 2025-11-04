"""
Bot do Telegram para Assistente Financeiro
Integração completa: Telegram + Gemini + Supabase
"""

import os
import sys
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.gemini_classifier import GeminiClassifier
from database.supabase_client import SupabaseClient


class FinanceBot:
    def __init__(self, token: str, gemini_key: str, supabase_url: str, supabase_key: str):
        """
        Inicializa o bot financeiro
        
        Args:
            token: Token do bot do Telegram
            gemini_key: API Key do Gemini
            supabase_url: URL do Supabase
            supabase_key: Service role key do Supabase
        """
        self.token = token
        
        # Inicializar componentes
        print("🔄 Inicializando componentes...")
        try:
            self.classificador = GeminiClassifier(api_key=gemini_key)
            self.db = SupabaseClient(url=supabase_url, key=supabase_key)
            print("✅ Gemini e Supabase conectados!\n")
        except Exception as e:
            print(f"❌ Erro ao inicializar componentes: {e}")
            raise
        
        # Criar aplicação
        self.app = Application.builder().token(self.token).build()
        
        # Registrar handlers
        self._registrar_handlers()
    
    def _registrar_handlers(self):
        """Registra todos os comandos e handlers do bot"""
        
        # Comandos
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("ajuda", self.cmd_ajuda))
        self.app.add_handler(CommandHandler("saldo", self.cmd_saldo))
        self.app.add_handler(CommandHandler("categoria", self.cmd_categoria))
        self.app.add_handler(CommandHandler("ultimos", self.cmd_ultimos))
        self.app.add_handler(CommandHandler("mes", self.cmd_mes))
        self.app.add_handler(CommandHandler("categorias", self.cmd_categorias))
        
        # Handler para mensagens de texto (transações)
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.processar_transacao)
        )
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Boas-vindas"""
        
        mensagem = """
👋 *Olá! Bem-vindo ao seu Assistente Financeiro!*

Eu vou te ajudar a controlar seus gastos e receitas de forma simples.

📝 *Como usar:*
Apenas envie mensagens naturais sobre seus gastos ou receitas, como:
• "Gastei 45 reais no almoço"
• "Uber pro trabalho 23,50"
• "Recebi 3000 de salário"

🤖 Eu vou entender automaticamente e registrar para você!

📊 *Comandos disponíveis:*
/ajuda - Ver todos os comandos
/saldo - Ver resumo do mês
/ultimos - Últimas 5 transações
/categoria [nome] - Gastos por categoria
/mes - Relatório completo do mês
/categorias - Lista de categorias

💡 *Dica:* Seja específico! Quanto mais detalhes, melhor eu consigo classificar.

Vamos começar? Envie sua primeira transação! 🚀
"""
        await update.message.reply_text(mensagem, parse_mode='Markdown')
    
    async def cmd_ajuda(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ajuda - Lista de comandos"""
        
        mensagem = """
📚 *GUIA DE COMANDOS*

*Comandos Principais:*
/start - Iniciar o bot
/ajuda - Mostrar esta mensagem
/saldo - Resumo financeiro do mês
/ultimos - Últimas 5 transações
/mes - Relatório completo do mês

*Consultas:*
/categoria [nome] - Ver gastos de uma categoria específica
  Exemplo: /categoria alimentação

/categorias - Ver lista de todas as categorias disponíveis

*Como registrar transações:*
Basta enviar mensagens naturais! Exemplos:

💸 *Gastos:*
• "Gastei 50 no mercado"
• "Uber 25 reais"
• "Paguei 150 de luz"
• "Almoço 35"

💰 *Receitas:*
• "Recebi 3000 de salário"
• "Freela 500 reais"
• "Vendi notebook por 2000"

🎯 *Dicas:*
✅ Mencione o valor claramente
✅ Inclua o que foi (almoço, uber, etc)
✅ Seja natural, eu entendo!

Dúvidas? Só perguntar! 😊
"""
        await update.message.reply_text(mensagem, parse_mode='Markdown')
    
    async def cmd_saldo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /saldo - Mostra resumo do mês"""
        
        await update.message.reply_text("🔄 Calculando seu saldo...")
        
        try:
            saldo = self.db.calcular_saldo_mes_atual()
            
            receitas = saldo['total_receitas']
            gastos = saldo['total_gastos']
            saldo_final = saldo['saldo']
            
            # Emoji baseado no saldo
            emoji_saldo = "🟢" if saldo_final >= 0 else "🔴"
            
            mensagem = f"""
💰 *RESUMO FINANCEIRO - {datetime.now().strftime('%B/%Y').upper()}*

💵 Receitas: R$ {receitas:,.2f}
💸 Gastos: R$ {gastos:,.2f}
{'─' * 25}
{emoji_saldo} *Saldo: R$ {saldo_final:,.2f}*
"""
            
            # Adicionar insights
            if gastos > 0:
                percentual_gasto = (gastos / receitas * 100) if receitas > 0 else 0
                
                if percentual_gasto > 90:
                    mensagem += "\n\n⚠️ Atenção! Você gastou mais de 90% das suas receitas."
                elif percentual_gasto > 70:
                    mensagem += "\n\n⚡ Cuidado! Seus gastos já passaram de 70% das receitas."
                elif percentual_gasto < 50:
                    mensagem += "\n\n✨ Parabéns! Você está economizando bem este mês."
            
            await update.message.reply_text(mensagem, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Erro ao calcular saldo: {e}")
    
    async def cmd_categoria(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /categoria - Mostra gastos por categoria"""
        
        # Verificar se categoria foi especificada
        if not context.args:
            # Mostrar todas as categorias
            categorias = self.db.gastos_por_categoria_mes_atual()
            
            if not categorias:
                await update.message.reply_text("📭 Nenhum gasto registrado ainda neste mês.")
                return
            
            mensagem = f"📊 *GASTOS POR CATEGORIA - {datetime.now().strftime('%B/%Y').upper()}*\n\n"
            
            # Ordenar por valor (maior para menor)
            for categoria, valor in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
                mensagem += f"• *{categoria.capitalize()}:* R$ {valor:,.2f}\n"
            
            total = sum(categorias.values())
            mensagem += f"\n{'─' * 25}\n💸 *Total:* R$ {total:,.2f}"
            
            await update.message.reply_text(mensagem, parse_mode='Markdown')
        
        else:
            # Mostrar categoria específica
            categoria = " ".join(context.args).lower()
            
            transacoes = self.db.buscar_por_categoria(categoria)
            
            if not transacoes:
                await update.message.reply_text(
                    f"📭 Nenhuma transação encontrada na categoria '{categoria}'."
                )
                return
            
            # Filtrar apenas gastos do mês atual
            hoje = datetime.now()
            inicio_mes = datetime(hoje.year, hoje.month, 1)
            
            gastos_mes = [
                t for t in transacoes 
                if t['tipo'] == 'gasto' and 
                datetime.fromisoformat(t['data'].replace('Z', '+00:00')) >= inicio_mes
            ]
            
            if not gastos_mes:
                await update.message.reply_text(
                    f"📭 Nenhum gasto em '{categoria}' neste mês."
                )
                return
            
            total = sum(t['valor'] for t in gastos_mes)
            
            mensagem = f"📂 *CATEGORIA: {categoria.upper()}*\n\n"
            mensagem += f"🗓️ Mês atual: {datetime.now().strftime('%B/%Y')}\n"
            mensagem += f"📊 Total de gastos: {len(gastos_mes)}\n"
            mensagem += f"💸 Valor total: R$ {total:,.2f}\n\n"
            mensagem += "📝 *Últimas transações:*\n"
            
            for t in gastos_mes[:5]:
                data = datetime.fromisoformat(t['data'].replace('Z', '+00:00'))
                mensagem += f"• R$ {t['valor']:.2f} - {t['descricao']}\n"
                mensagem += f"  _{data.strftime('%d/%m às %H:%M')}_\n"
            
            await update.message.reply_text(mensagem, parse_mode='Markdown')
    
    async def cmd_ultimos(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ultimos - Mostra últimas transações"""
        
        await update.message.reply_text("🔍 Buscando últimas transações...")
        
        try:
            transacoes = self.db.buscar_ultimas_transacoes(5)
            
            if not transacoes:
                await update.message.reply_text("📭 Nenhuma transação registrada ainda.")
                return
            
            mensagem = "📝 *ÚLTIMAS TRANSAÇÕES*\n\n"
            
            for t in transacoes:
                # Emoji baseado no tipo
                emoji = "💸" if t['tipo'] == 'gasto' else "💰"
                sinal = "-" if t['tipo'] == 'gasto' else "+"
                
                # Formatação da data
                data = datetime.fromisoformat(t['data'].replace('Z', '+00:00'))
                data_str = data.strftime('%d/%m às %H:%M')
                
                mensagem += f"{emoji} *{t['descricao']}*\n"
                mensagem += f"   {sinal} R$ {t['valor']:.2f} • {t['categoria']}\n"
                mensagem += f"   _{data_str}_\n\n"
            
            await update.message.reply_text(mensagem, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Erro ao buscar transações: {e}")
    
    async def cmd_mes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /mes - Relatório completo do mês"""
        
        await update.message.reply_text("📊 Gerando relatório do mês...")
        
        try:
            # Buscar dados do mês
            hoje = datetime.now()
            inicio_mes = datetime(hoje.year, hoje.month, 1)
            transacoes = self.db.buscar_por_periodo(inicio_mes, hoje)
            
            if not transacoes:
                await update.message.reply_text("📭 Nenhuma transação neste mês.")
                return
            
            # Calcular totais
            receitas = [t for t in transacoes if t['tipo'] == 'receita']
            gastos = [t for t in transacoes if t['tipo'] == 'gasto']
            
            total_receitas = sum(t['valor'] for t in receitas)
            total_gastos = sum(t['valor'] for t in gastos)
            saldo = total_receitas - total_gastos
            
            # Gastos por categoria
            categorias = {}
            for g in gastos:
                cat = g['categoria']
                categorias[cat] = categorias.get(cat, 0) + g['valor']
            
            # Montar mensagem
            emoji_saldo = "🟢" if saldo >= 0 else "🔴"
            mes_nome = hoje.strftime('%B/%Y').upper()
            
            mensagem = f"📊 *RELATÓRIO COMPLETO - {mes_nome}*\n\n"
            
            # Resumo geral
            mensagem += "💰 *RESUMO GERAL*\n"
            mensagem += f"💵 Receitas: R$ {total_receitas:,.2f} ({len(receitas)} itens)\n"
            mensagem += f"💸 Gastos: R$ {total_gastos:,.2f} ({len(gastos)} itens)\n"
            mensagem += f"{'─' * 25}\n"
            mensagem += f"{emoji_saldo} *Saldo: R$ {saldo:,.2f}*\n\n"
            
            # Gastos por categoria
            if categorias:
                mensagem += "📂 *GASTOS POR CATEGORIA*\n"
                for cat, valor in sorted(categorias.items(), key=lambda x: x[1], reverse=True)[:5]:
                    percentual = (valor / total_gastos * 100) if total_gastos > 0 else 0
                    mensagem += f"• {cat.capitalize()}: R$ {valor:,.2f} ({percentual:.0f}%)\n"
                
                if len(categorias) > 5:
                    mensagem += f"• ... e mais {len(categorias) - 5} categorias\n"
            
            # Média diária
            dias_passados = (hoje - inicio_mes).days + 1
            media_gasto_dia = total_gastos / dias_passados if dias_passados > 0 else 0
            
            mensagem += f"\n📈 *ESTATÍSTICAS*\n"
            mensagem += f"📅 Dias decorridos: {dias_passados}\n"
            mensagem += f"💸 Média de gasto/dia: R$ {media_gasto_dia:,.2f}\n"
            
            # Insight
            if total_receitas > 0:
                percentual_gasto = (total_gastos / total_receitas * 100)
                mensagem += f"📊 Você gastou {percentual_gasto:.1f}% das receitas\n"
            
            await update.message.reply_text(mensagem, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Erro ao gerar relatório: {e}")
    
    async def cmd_categorias(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /categorias - Lista todas as categorias disponíveis"""
        
        categorias = {
            "🍔 Alimentação": "restaurante, mercado, lanche, comida",
            "🚗 Transporte": "uber, ônibus, gasolina, taxi",
            "🏠 Moradia": "aluguel, condomínio, luz, água",
            "💊 Saúde": "médico, farmácia, remédio, exame",
            "📚 Educação": "curso, livro, faculdade, escola",
            "🎮 Lazer": "cinema, viagem, passeio, diversão",
            "👕 Vestuário": "roupa, sapato, acessório",
            "💻 Tecnologia": "celular, computador, software",
            "📱 Contas": "telefone, streaming, assinaturas",
            "📈 Investimentos": "ações, fundos, aplicações",
            "💰 Salário": "pagamento mensal, remuneração",
            "💼 Freelance": "trabalho extra, bico, serviços",
            "🛍️ Vendas": "venda de produtos ou itens",
            "📦 Outros": "qualquer outra coisa"
        }
        
        mensagem = "📂 *CATEGORIAS DISPONÍVEIS*\n\n"
        mensagem += "Eu classifico automaticamente suas transações nestas categorias:\n\n"
        
        for categoria, exemplos in categorias.items():
            mensagem += f"*{categoria}*\n_{exemplos}_\n\n"
        
        mensagem += "💡 *Dica:* Você não precisa especificar a categoria, "
        mensagem += "eu descubro automaticamente pela sua mensagem!"
        
        await update.message.reply_text(mensagem, parse_mode='Markdown')
    
    async def processar_transacao(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa mensagens de transações"""
        
        mensagem_usuario = update.message.text
        
        # Mensagem de processamento
        msg_processando = await update.message.reply_text("🤖 Analisando sua transação...")
        
        try:
            # Passo 1: Classificar com Gemini
            resultado = self.classificador.classificar(mensagem_usuario)
            
            if not resultado:
                await msg_processando.edit_text(
                    "❌ Não consegui entender sua mensagem.\n\n"
                    "💡 Tente ser mais específico, incluindo:\n"
                    "• O valor (ex: 50 reais)\n"
                    "• O que foi (ex: almoço, uber)\n\n"
                    "Exemplo: 'Gastei 45 no almoço'"
                )
                return
            
            # Verificar confiança
            if resultado['confianca'] < 0.5:
                await msg_processando.edit_text(
                    f"⚠️ Entendi, mas não tenho certeza...\n\n"
                    f"Você quis dizer:\n"
                    f"• Tipo: {resultado['tipo']}\n"
                    f"• Valor: R$ {resultado['valor']:.2f}\n"
                    f"• Categoria: {resultado['categoria']}\n\n"
                    f"Se estiver errado, tente reformular sua mensagem."
                )
            
            # Passo 2: Salvar no Supabase
            transacao = self.db.inserir_transacao(
                tipo=resultado['tipo'],
                valor=resultado['valor'],
                categoria=resultado['categoria'],
                descricao=resultado['descricao']
            )
            
            if not transacao:
                await msg_processando.edit_text("❌ Erro ao salvar no banco de dados.")
                return
            
            # Passo 3: Confirmação
            emoji = "💸" if resultado['tipo'] == 'gasto' else "💰"
            tipo_texto = "GASTO" if resultado['tipo'] == 'gasto' else "RECEITA"
            
            mensagem_confirmacao = f"{emoji} *{tipo_texto} REGISTRADO!*\n\n"
            mensagem_confirmacao += f"💵 Valor: R$ {resultado['valor']:.2f}\n"
            mensagem_confirmacao += f"📂 Categoria: {resultado['categoria']}\n"
            mensagem_confirmacao += f"📝 Descrição: {resultado['descricao']}\n"
            
            # Adicionar saldo atualizado
            saldo = self.db.calcular_saldo_mes_atual()
            mensagem_confirmacao += f"\n{'─' * 25}\n"
            mensagem_confirmacao += f"💰 Saldo do mês: R$ {saldo['saldo']:.2f}"
            
            await msg_processando.edit_text(mensagem_confirmacao, parse_mode='Markdown')
            
        except Exception as e:
            await msg_processando.edit_text(f"❌ Erro ao processar: {e}")
    
    def iniciar(self):
        """Inicia o bot"""
        print("🤖 Bot do Telegram iniciado!")
        print("📱 Aguardando mensagens...\n")
        print("Pressione Ctrl+C para parar\n")
        
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Função principal"""
    
    print("=" * 70)
    print("🤖 ASSISTENTE FINANCEIRO - BOT TELEGRAM")
    print("=" * 70 + "\n")
    
    # Carregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    # Obter credenciais
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Validar credenciais
    if not all([TELEGRAM_TOKEN, GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
        print("❌ Erro: Variáveis de ambiente faltando!")
        print("\nConfigure no arquivo .env:")
        print("  TELEGRAM_BOT_TOKEN=seu_token")
        print("  GEMINI_API_KEY=sua_key")
        print("  SUPABASE_URL=sua_url")
        print("  SUPABASE_KEY=sua_key")
        return
    
    try:
        # Criar e iniciar bot
        bot = FinanceBot(
            token=TELEGRAM_TOKEN,
            gemini_key=GEMINI_API_KEY,
            supabase_url=SUPABASE_URL,
            supabase_key=SUPABASE_KEY
        )
        
        bot.iniciar()
        
    except KeyboardInterrupt:
        print("\n\n👋 Bot encerrado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")


if __name__ == "__main__":
    main()