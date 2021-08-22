import discord
from discord.ext import commands
from . import Interface, Commands
from .tools import Tools

class Bot(commands.Bot):
    
    def __init__(self, remove_commands:list=[], *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Carregando bot em Interface
        Interface.load_bot(self)
        # Carregando comandos
        Commands.load(self, remove_commands=remove_commands)


    # Quando o BOT for Inciado
    async def on_ready(self) -> None:
        # Mensagem Inicial
        print('BOT iniciado: {0}!'.format(self.user))

        # Criando loop assíncrono executado a cada 60seg
        loop = Tools.AsyncLoop("Loop Principal [1]", sleep_secs=60)
        loop.add(Interface.change_status)#.run()
        # Rodando Loop
        super_loop = Tools.AsyncLoop("Super Loop")
        super_loop.add_all(loop)
        await super_loop.super_run()


    # Quando uma mensagem for enviada
    async def on_message(self, message:discord.Message) -> None:
        # Ativar manualmente processamento de comandos
        await self.process_commands(message)
        
        # Reações automáticas com base na mensagem
        await Interface.automatic_reaction_emojis(message, only_guild=False)
        
        # Interpreta código python nas mensagens caso o BOT seja mencionado
        await Interface.code_interpreter(message, only_guild=True)


    # Quando um comando inválido for enviado
    async def on_command_error(
        self, ctx:commands.Context, exception:Exception
    ) -> None:
        # Verifica se o comando retorna algum
        # resultado da documentação python
        await Interface.search_pydoc(ctx, ctx.invoked_with)


    # Quando um novo membro entrar no servidor
    async def on_member_join(self, member:discord.Member):
        # Enviando boas vindas ao novo membro
        await Interface.welcome_dm_message(member)
