import discord
from src.PyBrBot import Bot, Config

# Solicitando modo do BOT
test_mode = input("Ativar modo teste? (S/n) ")

# Ativa o modo oficial caso ativação seja negada
if (test_mode.lower() in ["n", "nao", "não"]):
    test_mode = False
    token = Config.get('token')
    command_prefix = Config.get('bot_commands_prefix')
else:
    test_mode = True
    token = Config.get('test_token')
    command_prefix = Config.get('test_bot_commands_prefix')

# Inciando BOT
if (__name__ == "__main__"):
    # Alterando intents
    intents = discord.Intents.default()
    intents.members = True
    
    client = Bot(
        intents=intents,
        command_prefix=command_prefix, 
        remove_commands=['help']
    )
    client.run(token)
