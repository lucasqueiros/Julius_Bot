# 🚀 Guia Rápido de Deploy - Vercel

## Passo a Passo em 5 minutos

### 1️⃣ Preparar o Projeto

```bash
# Certifique-se de que todos os arquivos estão commitados
git add .
git commit -m "Configurado para webhook na Vercel"
git push origin main
```

### 2️⃣ Deploy na Vercel

**Via Dashboard (Mais fácil):**

1. Acesse: https://vercel.com/new
2. Importe seu repositório GitHub
3. Adicione as 4 variáveis de ambiente:
   - `TELEGRAM_BOT_TOKEN`
   - `GEMINI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
4. Clique em **Deploy**
5. Anote a URL gerada (ex: `julius-bot.vercel.app`)

**Via CLI (Alternativa):**

```bash
# Instalar CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Adicionar variáveis
vercel env add TELEGRAM_BOT_TOKEN
vercel env add GEMINI_API_KEY
vercel env add SUPABASE_URL
vercel env add SUPABASE_KEY

# Deploy em produção
vercel --prod
```

### 3️⃣ Configurar Webhook

**Opção A: Script automático**

```bash
python setup_webhook.py
# Escolha opção 1
# Digite: https://sua-url.vercel.app/api/webhook
```

**Opção B: Manual (substitua <TOKEN> e <URL>)**

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://<SUA-URL>.vercel.app/api/webhook"}'
```

### 4️⃣ Testar

1. Abra o Telegram
2. Procure seu bot
3. Envie: `/start`
4. Teste: "Gastei 50 no almoço"

✅ **Pronto! Seu bot está online!**

---

## 📋 Checklist

- [ ] Código commitado no GitHub
- [ ] Deploy feito na Vercel
- [ ] 4 variáveis de ambiente configuradas
- [ ] URL do webhook anotada
- [ ] Webhook configurado via script ou curl
- [ ] Bot testado e respondendo

---

## ⚠️ Problemas Comuns

### Bot não responde?

```bash
# Verificar webhook
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# Ver logs
# Dashboard Vercel → Functions → /api/webhook
```

### Erro 500?

- Verifique se TODAS as 4 variáveis estão configuradas
- Veja os logs na Vercel
- Teste o endpoint: `curl https://sua-url.vercel.app/api/webhook`

### Mensagens antigas aparecendo?

```bash
# Limpar fila
python setup_webhook.py
# Opção 1 → URL do webhook (reconfigura e limpa)
```

---

## 🔄 Desenvolvimento Local

Para testar localmente:

```bash
# 1. REMOVER webhook primeiro
python setup_webhook.py  # Opção 3

# 2. Executar em modo polling
python bot/telegram_bot.py
```

**⚠️ Não use polling e webhook ao mesmo tempo!**

---

## 📞 Precisa de ajuda?

- Leia: [README_VERCEL.md](README_VERCEL.md)
- Issues: https://github.com/lucasqueiros/Julius_Bot/issues
