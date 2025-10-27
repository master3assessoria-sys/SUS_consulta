import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Token seguro via variável de ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")

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
    await update.message.reply_text(" ", reply_markup=reply_markup)

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
        "/ajuda – Mostrar esta mensagem\n"
        "/consulta – Solicitar agendamento de consulta\n"
        "/exames – Agendar exames\n"
        "/resultado – Ver resultado dos exames\n"
        "/unidades – Informações sobre unidades SUS\n"
        "/especialista – Encaminhamento para especialista\n"
        "/menu – Mostrar botões interativos\n"
        "/minhasconsultas – Ver suas consultas agendadas"
    )
    await mostrar_menu(update)

async def consulta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario_id = update.effective_user.id
    if usuario_id not in usuarios_dados or "nome" not in usuarios_dados[usuario_id]:
        await update.message.reply_text("Você precisa informar seu CPF e nome antes de agendar uma consulta. Use /cpf 12345678900")
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
    await update.message.reply_text(
        "Vamos agendar seus exames.\n"
        "Use o comando /consulta para iniciar o agendamento guiado."
    )
    await mostrar_menu(update)

async def minhasconsultas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario_id = update.effective_user.id
    if usuario_id not in usuarios_dados:
        await update.message.reply_text("Você precisa informar seu CPF antes de consultar seus agendamentos. Use /cpf 12345678900")
        return
    consultas = [c for c in agendamentos_registrados if c["usuario_id"] == usuario_id]
    if not consultas:
        await update.message.reply_text("Você ainda não possui consultas agendadas.")
        await mostrar_menu(update)
        return
    resposta = "Suas consultas agendadas:\n\n"
    for c in consultas:
        resposta += (
            f"Data: {c['data']} às {c['hora']}\n"
            f"Unidade: {c['unidade']}\n"
            f"Especialidade: {c['especialidade']}\n"
            f"Intérprete de Libras: {c['libras'].capitalize()}\n"
            f"Nome: {c['nome']}\n"
            f"CPF: {c['cpf']}\n\n"
        )
    await update.message.reply_text(resposta)
    await mostrar_menu(update)

async def resultado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Resultado dos exames alterado. Encaminhando para consulta médica.\n"
        "Após a consulta, será definido:\n"
        "- Tratamento clínico\n"
        "- Ou encaminhamento para serviço especializado\n"
        "O processo continua até que o caso seja encerrado com alta médica."
    )
    await mostrar_menu(update)

async def unidades(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Solicitação de atendimento nas unidades SUS:\n"
        "1. Você solicita o atendimento\n"
        "2. Se não tiver cadastro, será realizado na hora\n"
        "3. Após isso, o atendimento será iniciado normalmente"
    )
    await mostrar_menu(update)

async def especialista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Consulta médica realizada. Avaliando necessidade de especialista.\n"
        "Se necessário, será feito o encaminhamento para regulação e agendamento com especialista.\n"
        "Caso não seja necessário, o atendimento será encerrado."
    )
    await mostrar_menu(update)

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mostrar_menu(update)

async def nlp_resposta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    usuario_id = update.effective_user.id

    if usuario_id not in etapas_agendamento and texto.strip() in ["ok", "obrigado", "valeu"]:
        await update.message.reply_text("Fico à disposição. Se precisar, digite /menu para ver as opções.")
        return

    if usuario_id in usuarios_dados and "nome" not in usuarios_dados[usuario_id]:
        if len(texto.strip().split()) < 2:
            await update.message.reply_text("Por favor, informe seu nome completo (nome e sobrenome).")
            return
        usuarios_dados[usuario_id]["nome"] = texto.strip().title()
        await update.message.reply_text(
            f"Nome registrado: {usuarios_dados[usuario_id]['nome']}.\n"
            "Como posso te ajudar hoje?\n"
            "- quero marcar consulta\n"
            "- preciso de exame\n"
            "- solicitar intérprete de Libras\n"
            "- ver minhas consultas"
        )
        return

    if usuario_id in etapas_agendamento:
        etapa = etapas_agendamento[usuario_id]
        if etapa.get("etapa") == "unidade":
            try:
                escolha = int(texto.strip())
                if 1 <= escolha <= len(unidades_disponiveis):
                    etapa["unidade"] = unidades_disponiveis[escolha - 1]
                    etapa["etapa"] = "libras"
                    await update.message.reply_text("Deseja agendar com intérprete de Libras?\n1. Sim\n2. Não")
                    return
                else:
                    await update.message.reply_text("Número inválido. Tente novamente.")
                    return
            except:
                await update.message.reply_text("Digite apenas o número da unidade desejada.")
                return

        elif etapa.get("etapa") == "libras":
            if texto.strip() == "1":
                etapa["libras"] = "Sim"
            elif texto.strip() == "2":
                etapa["libras"] = "Não"
            else:
                await update.message.reply_text("Escolha 1 para Sim ou 2 para Não.")
                return
            etapa["etapa"] = "data"
            datas = list(datas_disponiveis.keys())
            texto = "Escolha uma data disponível para sua consulta:\n"
            for i, d in enumerate(datas):
                texto += f"{i+1}. {d}\n"
            texto += "Digite o número da data desejada."
            await update.message.reply_text(texto)
            return

        elif etapa.get("etapa") == "data
