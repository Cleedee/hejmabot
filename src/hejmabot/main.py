from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from hejmatbot import EstoqueAPI

api = EstoqueAPI()


async def estoque(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        itens = await api.listar_itens()
        if not itens:
            await update.message.reply_text("O estoque está vazio! 📭")
            return

        mensagem = "**📦 Estoque Atual:**\n\n"
        for item in itens:
            mensagem += f"• {item['nome']}: {item['quantidade']} {item['unidade']}\n"

        await update.message.reply_text(mensagem, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Erro ao conectar na API: {e}")


if __name__ == "__main__":
    # Substitua pelo seu Token real
    app = ApplicationBuilder().token("SEU_TOKEN_AQUI").build()
    app.add_handler(CommandHandler("estoque", estoque))
    print("Hejmabot online e vigiando a despensa...")
    app.run_polling()
