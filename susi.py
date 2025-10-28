import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Token seguro via variável de ambiente
BOT_TOKEN = os.getenv("TOKEN")

usuarios_dados = {}
agendamentos_registrados = []
etapas_agendamento = {}

datas_disponiveis = {
    "27/10/2025": ["10h00", "11h00", "14h00"],
    "28/10/2025": ["09h00", "13h00", "15h00"],
    "29/10/2025": ["08h30", "10h30", "16h00"]
}

unidades_disponiveis = ["Zona Norte", "Zona Sul", "Zona Oeste"]

async def mostrar_menu(update: Update):
    teclado = [["/consulta", "/exames"], ["/resultado", "/especialista"], ["/unidades", "/ajuda"]]
    reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)
    await update.message.reply_text("Escolha uma opção:", reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Bem-vindo ao SUSi, {update.effective_user.first_name}. Para continuar, digite seu CPF usando o comando:\n"
        "/cpf 12345678900"
    )

async def cpf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        cpf_valor = context.args[0]
        if not cpf_valor.isdigit() or len(cpf_valor) != 11:
            await update.message.reply_text("CPF inválido. Envie apenas os 11 números, sem pontos ou traços.")
            return
        usuario_id = update.effective_user.id
        usuarios_dados[usuario_id] = {"cpf": cpf_valor}
        await update.message.reply_text("CPF registrado com sucesso.\nAgora, por favor, informe seu nome completo.")
    except:
        await update.message.reply_text("Por favor, envie o CPF no formato: /cpf 12345678900")

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Comandos disponíveis:\n"
        "/start – Inicia o bot\n"
        "/cpf – Registrar CPF\n"
        "/consulta – Agendar consulta\n"
        "/exames – Agendar exames\n"
        "/resultado – Ver resultado dos exames\n"
        "/unidades – Informações sobre unidades\n"
        "/especialista – Encaminhamento médico\n"
        "/minhasconsultas – Ver suas consultas\n"
        "/ajuda – Mostrar esta mensagem"
    )
    await mostrar_menu(update)

async def consulta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario_id = update.effective_user.id
    if usuario_id not in usuarios_dados or "nome" not in usuarios_dados[usuario_id]:
        await update.message.reply_text("Você precisa informar seu CPF e nome antes de agendar. Use /cpf.")
        return
    if usuario_id in etapas_agendamento:
        await update.message.reply_text("Você já está em processo de agendamento. Continue escolhendo as opções.")
        return
    etapas_agendamento[usuario_id] = {"etapa": "unidade"}
    texto = "Escolha uma unidade de atendimento:\n"
    for i, u in enumerate(unidades_disponiveis):
        texto += f"{i+1}. {u}\n"
    texto += "Digite o número da unidade desejada."
    await update.message.reply_text(texto)

async def exames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Para agendar exames, use o comando /
     
