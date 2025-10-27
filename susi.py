import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Token seguro via variável de ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")

# (todo o restante do seu código permanece igual, incluindo funções e comandos)

# Inicialização do bot
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("cpf", cpf))
app.add_handler(CommandHandler("ajuda", ajuda))
app.add_handler(CommandHandler("consulta", consulta))
app.add_handler(CommandHandler("exames", exames))
app.add_handler(CommandHandler("resultado", resultado))
app.add_handler(CommandHandler("unidades", unidades))
app.add_handler(CommandHandler("especialista", especialista))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("minhasconsultas", minhasconsultas))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, nlp_resposta))

print("Bot está funcionando")
app.run_polling()
