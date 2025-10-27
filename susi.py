# Inicialização do bot
app = ApplicationBuilder().token("8205835585:AAEbtURw7RJGswhxTqS-UZte6-CG2oQIXfY").build()

# Comandos
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

# Mensagens de texto
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, nlp_resposta))

print("Bot está funcionando")
app.run_polling()
