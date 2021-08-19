from typing import Union
import discord as ds
from discord.ext import commands
from .interface import Interface
from .config import Config
from .tools import AsyncFast, BotLoading


"""
Classe responsável pela criação e carregamento
dos comandos do BOT via prefixo
"""
class Commands:

    # Carrega os comandos criados em _commands
    # Permite remover algum(s) comandos via nome:str
    @staticmethod
    def load(
        bot:commands.Bot, remove_commands:Union[str, list]=[]
    ) -> None:
        Commands._commands(bot)
        Commands._remove(bot, remove_commands)


    # Permite remover comando(s) não utilizado(s)
    @staticmethod
    def _remove(
        bot:commands.Bot, commands:Union[str, list]=[]
    ) -> None:
        commands = [commands] if isinstance(commands, str) else commands
        
        for command in commands:
            bot.remove_command(command)

    
    # TODA CRIAÇÃO DE COMANDOS DEVE SER FEITA AQUI
    # Adiciona todos os comandos ao BOT
    @staticmethod
    def _commands(bot:commands.Bot) -> None:
        command = bot.command

        # Acessa a documentação python com busca
        @command()
        async def doc(ctx:ds.abc.Messageable, *, search:str=""):
            await Interface.search_pydoc(ctx, search)
