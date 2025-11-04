# 🤖 Julius Finance Bot - Deploy na Vercel

Bot de assistente financeiro para Telegram com integração Gemini AI e Supabase, configurado para rodar em modo **webhook** na Vercel.

## 📋 Índice

- [Pré-requisitos](#-pré-requisitos)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Deploy na Vercel](#-deploy-na-vercel)
- [Configuração do Webhook](#-configuração-do-webhook)
- [Desenvolvimento Local](#-desenvolvimento-local)
- [Variáveis de Ambiente](#-variáveis-de-ambiente)
- [Troubleshooting](#-troubleshooting)

## 🎯 Pré-requisitos

1. **Conta na Vercel** - [Criar conta gratuita](https://vercel.com/signup)
2. **Bot do Telegram** - Token obtido via [@BotFather](https://t.me/botfather)
3. **Google Gemini API** - [Obter API Key](https://makersuite.google.com/app/apikey)
4. **Supabase** - [Criar projeto gratuito](https://supabase.com)
5. **Vercel CLI** (opcional) - `npm i -g vercel`

## 📁 Estrutura do Projeto

```
Julius_Bot/
├── api/
│   └── webhook.py          # Endpoint serverless para webhook
├── bot/
│   ├── telegram_bot.py     # Lógica principal do bot
│   └── gemini_classifier.py # Classificador IA
├── database/
│   └── supabase_client.py  # Cliente do banco
├── dashboard/              # Dashboard Streamlit (não usado na Vercel)
│   └── streamlit_app.py
├── requirements.txt        # Dependências Python
├── vercel.json            # Configuração da Vercel
├── .vercelignore          # Arquivos ignorados no deploy
├── setup_webhook.py       # Script de configuração
└── README_VERCEL.md       # Este arquivo
```

## 🚀 Deploy na Vercel

### Opção 1: Via Dashboard da Vercel (Recomendado)

1. **Faça fork/clone do repositório**
   ```bash
   git clone https://github.com/lucasqueiros/Julius_Bot.git
   cd Julius_Bot
   ```

2. **Acesse o [Dashboard da Vercel](https://vercel.com/dashboard)**

3. **Clique em "New Project"**

4. **Importe seu repositório GitHub**
   - Conecte sua conta GitHub
   - Selecione o repositório `Julius_Bot`

5. **Configure as variáveis de ambiente** (Environment Variables):
   ```
   TELEGRAM_BOT_TOKEN=seu_token_do_telegram
   GEMINI_API_KEY=sua_chave_do_gemini
   SUPABASE_URL=sua_url_do_supabase
   SUPABASE_KEY=sua_service_key_do_supabase
   ```

6. **Deploy!**
   - Clique em "Deploy"
   - Aguarde o build finalizar
   - Anote a URL gerada (ex: `https://seu-app.vercel.app`)

### Opção 2: Via CLI da Vercel

```bash
# 1. Instalar Vercel CLI
npm i -g vercel

# 2. Login na Vercel
vercel login

# 3. Deploy
vercel

# 4. Adicionar variáveis de ambiente
vercel env add TELEGRAM_BOT_TOKEN
vercel env add GEMINI_API_KEY
vercel env add SUPABASE_URL
vercel env add SUPABASE_KEY

# 5. Deploy para produção
vercel --prod
```

## 🔗 Configuração do Webhook

Após o deploy, você precisa **registrar a URL do webhook** no Telegram:

### Método 1: Usando o script `setup_webhook.py`

```bash
# 1. Configurar variáveis de ambiente localmente
cp .env.example .env
# Edite o .env com seu TELEGRAM_BOT_TOKEN

# 2. Executar o script
python setup_webhook.py
```

Siga as instruções no terminal:
- Opção 1: Configurar webhook
- Informe a URL: `https://seu-app.vercel.app/api/webhook`

### Método 2: Manualmente via API do Telegram

```bash
curl -X POST "https://api.telegram.org/bot<SEU_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://seu-app.vercel.app/api/webhook",
    "max_connections": 100,
    "drop_pending_updates": true
  }'
```

### Verificar se o webhook está configurado

```bash
curl "https://api.telegram.org/bot<SEU_TOKEN>/getWebhookInfo"
```

Resposta esperada:
```json
{
  "ok": true,
  "result": {
    "url": "https://seu-app.vercel.app/api/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

## 💻 Desenvolvimento Local

Para testar localmente em modo **polling** (sem webhook):

```bash
# 1. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar .env
cp .env.example .env
# Edite com suas credenciais

# 4. Executar bot em modo polling
python bot/telegram_bot.py
```

**⚠️ IMPORTANTE:** Certifique-se de **remover o webhook** antes de usar polling localmente:

```bash
python setup_webhook.py
# Escolha opção 3: Remover webhook
```

## 🔐 Variáveis de Ambiente

Configure estas variáveis na Vercel:

| Variável | Descrição | Onde obter |
|----------|-----------|-----------|
| `TELEGRAM_BOT_TOKEN` | Token do bot do Telegram | [@BotFather](https://t.me/botfather) |
| `GEMINI_API_KEY` | Chave da API do Google Gemini | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| `SUPABASE_URL` | URL do projeto Supabase | Dashboard do Supabase → Settings → API |
| `SUPABASE_KEY` | Service Role Key do Supabase | Dashboard do Supabase → Settings → API |

### Como adicionar na Vercel:

1. Acesse seu projeto na Vercel
2. Vá em **Settings** → **Environment Variables**
3. Adicione cada variável
4. Marque todos os ambientes (Production, Preview, Development)
5. Clique em **Save**
6. Faça redeploy: **Deployments** → **...** → **Redeploy**

## 🐛 Troubleshooting

### Bot não responde

1. **Verifique se o webhook está configurado:**
   ```bash
   python setup_webhook.py  # Opção 2: Verificar status
   ```

2. **Veja os logs na Vercel:**
   - Dashboard → Seu projeto → Functions → Clique em `/api/webhook`
   - Veja os logs em tempo real

3. **Teste o endpoint:**
   ```bash
   curl https://seu-app.vercel.app/api/webhook
   ```
   Deve retornar: `{"status": "ok", "message": "Telegram Bot Webhook is running"}`

### Erro 500 no webhook

- Verifique se todas as variáveis de ambiente estão configuradas
- Veja os logs da função na Vercel
- Teste localmente primeiro

### Mensagens antigas sendo processadas

- Configure o webhook com `drop_pending_updates=true`
- Ou use o script: `python setup_webhook.py` → Opção 1

### Timeout da função

- Vercel tem limite de 10 segundos para funções no plano gratuito
- Operações pesadas do Gemini podem exceder
- Considere otimizar ou usar plano pago

### Polling e Webhook ao mesmo tempo

**NÃO FUNCIONA!** Você deve escolher um:

- **Webhook** → Para produção na Vercel
- **Polling** → Para desenvolvimento local

Sempre remova o webhook antes de usar polling:
```bash
python setup_webhook.py  # Opção 3: Remover webhook
```

## 📊 Dashboard

O dashboard Streamlit **não pode** ser hospedado na Vercel (Vercel é só para APIs/Next.js).

**Opções para o dashboard:**
- [Streamlit Cloud](https://streamlit.io/cloud) (grátis)
- [Railway](https://railway.app) (grátis com limites)
- [Render](https://render.com) (grátis com limites)

## 🔄 Atualizações

Após fazer alterações no código:

1. **Commit e push para GitHub**
   ```bash
   git add .
   git commit -m "Descrição da mudança"
   git push
   ```

2. **Deploy automático**
   - Vercel detecta automaticamente e faz redeploy
   - Acompanhe em: Dashboard → Deployments

## 📚 Recursos Úteis

- [Documentação Vercel](https://vercel.com/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Python Telegram Bot](https://python-telegram-bot.org/)
- [Google Gemini API](https://ai.google.dev/)
- [Supabase Docs](https://supabase.com/docs)

## 🆘 Suporte

Problemas? Abra uma [issue no GitHub](https://github.com/lucasqueiros/Julius_Bot/issues)

---

Feito com ❤️ por Lucas Queiros
