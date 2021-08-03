import discord
from src.PyBrBot import Interface, Config

# Solicitando modo e acessando Token
test_mode = input("Ativar modo teste? (S/n) ")
test_mode = False if test_mode.lower() in ["n", "nao", "não"] else True
token = Config.get('token') if not test_mode else Config.get('test_token')

# BOT
class PyBrBot(discord.Client):

    # Quando o BOT for Inciado
    async def on_ready(self) -> None:
        print('BOT iniciado: {0}!'.format(self.user))
        # Atualizando Status
        await Interface.change_status(self)

    # Quando uma mensagem for enviada
    async def on_message(self, message:discord.Message) -> None:
        # Reações automáticas com base na mensagem
        await Interface.automatic_reaction_emojis(self, message, only_guild=False)
        # Interpreta código python nas mensagens caso o BOT seja mencionado
        await Interface.code_interpreter(self, message, only_guild=True)

# Inciando
if (__name__ == "__main__"):
    client = PyBrBot()
    client.run(token)
