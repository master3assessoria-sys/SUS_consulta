import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

BOT_TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # ex: https://susi.onrender.com

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
    await update.message.reply_text("Para agendar exames, use o comando /consulta e siga as etapas.")
    await mostrar_menu(update)

async def resultado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Resultado dos exames alterado. Encaminhando para consulta médica.\n"
        "Após a consulta, será definido o tratamento ou encaminhamento para especialista."
    )
    await mostrar_menu(update)

async def unidades(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Atendimento nas unidades SUS:\n"
        "1. Solicitação\n2. Cadastro (se necessário)\n3. Atendimento"
    )
    await mostrar_menu(update)

async def especialista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Consulta médica realizada. Avaliando necessidade de especialista.\n"
        "Encaminhamento será feito se necessário."
    )
    await mostrar_menu(update)

async def minhasconsultas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario_id = update.effective_user.id
    if usuario_id not in usuarios_dados:
        await update.message.reply_text("Informe seu CPF antes de consultar agendamentos. Use /cpf.")
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

async def nlp_resposta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    usuario_id = update.effective_user.id

    if usuario_id not in etapas_agendamento and texto.strip() in ["ok", "obrigado", "valeu"]:
        await update.message.reply_text("Fico à disposição. Digite /menu para ver as opções.")
        return

    if usuario_id in usuarios_dados and "nome" not in usuarios_dados[usuario_id]:
        if len(texto.strip().split()) < 2:
            await update.message.reply_text("Informe seu nome completo (nome e sobrenome).")
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

        elif etapa.get("etapa") == "data":
            try:
                escolha = int(texto.strip())
                datas = list(datas_disponiveis.keys())
                if 1 <= escolha <= len(datas):
                    etapa["data"] = datas[escolha - 1]
                    etapa["etapa"] = "hora"
                    horarios = datas_disponiveis[etapa["data"]]
                    resposta = f"Você escolheu {etapa['data']}.\nEscolha um horário:\n"
                    for i, h in enumerate(horarios):
                        resposta += f"{i+1}. {h}\n"
                    resposta += "Digite o número do horário desejado."
                    await update.message.reply_text(resposta)
                    return
                else:
                    await update.message.reply_text("Número inválido. Tente novamente.")
                    return
            except:
                await update.message.reply_text("Digite apenas o número da data desejada.")
                return

        elif etapa.get("etapa") == "hora":
            try:
                escolha = int(texto.strip())
                horarios = datas_disponiveis[etapa["data"]]
                if 1 <= escolha <= len(horarios):
                    etapa["hora"] = horarios[escolha - 1]
                    etapa["especialidade"] = "Clínico Geral"
                    etapa["cpf"] = usuarios_dados[usuario_id]["cpf"]
                    etapa["nome"] = usuarios_dados[usuario_id]["nome"]
                    etapa["usuario_id"] = usuario_id
                    agendamentos_registrados.append(etapa)
                    del etapas_agendamento[usuario_id]
                    await update.message.reply_text(
                        f"Consulta agendada com sucesso!\n\n"
                        f"Nome: {etapa['nome']}\n"
                        f"CPF: {etapa['cpf']}\n"
                        f"Unidade: {etapa['unidade']}\n"
                        f"Data: {etapa['data']} às {etapa['hora']}\n"
                        f"Especialidade: {etapa['especialidade']}\n"
                        f"Intérprete de Libras: {etapa['libras']}"
                    )
                    await mostrar_menu(update)
                    return
                else:
                    await update.message.reply_text("Número inválido. Tente novamente.")
                    return
            except:
                await update.message.reply_text("Digite apenas o número do horário desejado.")
                return

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cpf", cpf))
    app.add_handler(CommandHandler("ajuda", ajuda))
    app.add_handler(CommandHandler("consulta", consulta))
    app.add_handler(CommandHandler("exames", exames))
    app.add_handler(CommandHandler("resultado", resultado))
    app.add_handler(CommandHandler("unidades", unidades))
    app.add_handler(CommandHandler("especialista", especialista))
    app.add_handler(CommandHandler("minhasconsultas", minhasconsultas))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, nlp_resposta))

    print("Bot está funcionando", flush=True)

   app.run_polling()

