import os
from datetime import datetime, time, date
from dotenv import load_dotenv 

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from hejmabot.api_client import EstoqueAPI
from hejmabot.nlp_processor import ProcessadorUniversal, AnalistaEconomico

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("API_URL", "http://127.0.0.1:8081")
CHAT_ID_PESSOAL = os.getenv("CHAT_ID_PESSOAL")

api = EstoqueAPI(base_url=API_URL)

nlp = ProcessadorUniversal()

async def gerar_relatorio_mensal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 O Ollama está analisando seu consumo do último mês..."
    )
    try:
        # 1. Busca dados na API
        historico = api.buscar_historico_consumo()

        # 2. IA analisa
        analista = AnalistaEconomico()
        analise = analista.analisar_gastos(historico)

        await update.message.reply_text(
            f"📊 **Relatório de Consumo Local:**\n\n{analise}", parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"Erro ao gerar relatório: {e}")


async def processar_mensagem_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text
    status_msg = await update.message.reply_text("🧠 Analisando sua entrada...")

    try:

        dados_extraidos = await nlp.processar_entrada(texto_usuario)
        assert dados_extraidos is not None
        local = dados_extraidos.get("local_compra")
        itens = dados_extraidos.get("itens", [])

        for item in itens:
            if local and not item.get("local_compra"):
                item["estabelecimento"] = local

            await api.adicionar_item(item)

        resumo = f"✅ Sucesso! {len(itens)} itens registrados"
        if local:
            resumo += f" no {local}."

        await status_msg.edit_text(resumo)

    except Exception as e:
        await status_msg.edit_text(f"❌ Erro ao processar: {e}")


async def usar_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /usar [nome do item]")
        return

    busca = " ".join(context.args)

    # 1. Primeiro listamos para achar o ID (lógica simples de busca)
    itens = await api.listar_itens()
    item_encontrado = next(
        (i for i in itens if busca.lower() in i["nome"].lower()), None
    )

    if not item_encontrado:
        await update.message.reply_text(f"❌ Não encontrei '{busca}' no estoque ativo.")
        return

    # 2. Fazemos o PATCH na API
    try:
        async with httpx.AsyncClient() as client:
            # Note que usamos a API_URL do seu .env
            url = f"{API_URL}/itens/{item_encontrado['id']}/consumir"
            response = await client.patch(url)

            if response.status_code == 200:
                await update.message.reply_text(
                    f"✅ Baixa registada: {item_encontrado['nome']} saiu do stock."
                )
            else:
                await update.message.reply_text("❌ Erro ao atualizar no servidor.")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro de conexão: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    print(
        f"DEBUG: O Chat ID deste usuário é: {user_id}"
    )  # Vai aparecer no seu terminal
    await update.message.reply_text(
        "Olá! Sou o Hejmabot. Posso te ajudar a gerenciar seu estoque doméstico.\n"
        "Use /estoque para ver o que temos."
    )


async def estoque(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        itens = await api.listar_itens()
        if not itens:
            await update.message.reply_text("O estoque está vazio! 📭")
            return

        mensagem = "**📦 Estoque Atual:**\n\n"
        for item in itens:
            mensagem += (
                f"• {item['nome']}: {item['quantidade_atual']} {item['unidade']}\n"
            )

        await update.message.reply_text(mensagem, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Erro ao conectar na API: {e}")


async def checar_agora(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Verificando validades no backend...")
    await callback_validade(context)


# --- TAREFA AGENDADA ---
async def callback_validade(context: ContextTypes.DEFAULT_TYPE):
    """Função que será chamada pelo agendador"""
    try:
        # Busca itens que vencem nos próximos 5 dias
        alertas = await api.buscar_alertas(dias=5)

        if alertas:
            mensagem = "⚠️ **AGENTE DE SAÚDE DOMÉSTICA**\n\n"
            mensagem += "Identifiquei itens próximos do vencimento:\n"

            for item in alertas:
                # Cálculo simples de dias restantes
                validade = datetime.strptime(item["data_validade"], "%Y-%m-%d").date()
                hoje = date.today()
                dias_restantes = (validade - hoje).days

                status = "🔴" if dias_restantes <= 2 else "🟡"
                mensagem += (
                    f"{status} *{item['nome']}*: vence em {dias_restantes} dias\n"
                )

            mensagem += "\n_Sugestão: Que tal planejar o jantar com estes itens?_"

            await context.bot.send_message(
                chat_id=CHAT_ID_PESSOAL, text=mensagem, parse_mode="Markdown"
            )
    except Exception as e:
        print(f"Erro na verificação automática: {e}")


if __name__ == "__main__":
    if not TOKEN:
        print("Erro: TELEGRAM_TOKEN não encontrado no arquivo .env")
        exit(1)
    app = ApplicationBuilder().token(TOKEN).build()

    # 2. Configuração do Agendamento (JobQueue)
    job_queue = app.job_queue

    # Roda todo dia às 09:00 da manhã
    job_queue.run_daily(callback_validade, time=time(hour=9, minute=0, second=0))

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("estoque", estoque))
    app.add_handler(CommandHandler("checar", checar_agora))
    app.add_handler(CommandHandler("usar", usar_item))
    app.add_handler(CommandHandler("relatorio", gerar_relatorio_mensal))
    app.add_handler(CommandHandler("comer", comer_item))
    app.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), processar_mensagem_texto)
    )

    print(f"Hejmabot online (Conectado em {API_URL})...")
    app.run_polling()
