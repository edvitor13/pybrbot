import asyncio
from functools import partial
import discord as ds
from discord.utils import get
from .functions import Functions

"""
Classe responsável por intermediar as funcionalidades
de PyBrBot.Functions com o BOT
"""
class Interface:

    # Responsável pela execução assíncrona dos
    # métodos de Functions
    async def _async(function:callable, *args, **kwargs):
        return await asyncio.get_event_loop().run_in_executor(
            None, partial(function, *args, **kwargs)
        )
    
    async def _async_timeout(timeout:float, function:callable, *args, **kwargs):
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(
            None, partial(function, *args, **kwargs)
        )
        return await asyncio.wait_for(future, timeout, loop=loop)
    
    
    # Atualizando status
    async def change_status(
        bot:ds.Client, status_message:str=None
    ) -> None:
        tools = Functions()

        if (status_message is None):
            status_message = await Interface._async(
                tools.get_status
            )
        
        activity = ds.Game(name=status_message)
        await bot.change_presence(activity=activity)


    # Adiciona reações com base na mensagem
    async def automatic_reaction_emojis(
        bot:ds.Client, message:ds.Message, only_guild:bool=True
    ) -> None:
        # Verificar se aceitará mensagens diretas ao bot
        if (message.guild is None and only_guild):
            return None

        tools = Functions()

        # Caso o autor da mensagem não seja um bot
        if (not message.author.bot):
            # Armazena as reações com base na mensagem
            reactions = await Interface._async(
                tools.automatic_reaction_emojis, message.content
            )
            # Adiciona cada reação
            for reaction in reactions:
                add_reaction = get(bot.emojis, name=reaction)
                await message.add_reaction(emoji=add_reaction)

    
    # Interpreta código Python da mensagem
    async def code_interpreter(
        bot:ds.Client, message:ds.Message, only_guild:bool=True
    ) -> None:
        # Verificar se aceitará mensagens diretas ao bot
        if (message.guild is None and only_guild):
            return None
        
        tools = Functions()

        bot_mentioned = bot.user.mentioned_in(message)
        contain_pycode = "```py" in message.content

        if (
            bot_mentioned and contain_pycode and not message.author.bot
        ):
            try:
                code_interpreter = await Interface._async_timeout(
                    30, tools.code_interpreter, message.content
                )
            except:
                await message.channel.send("Não foi possível executar seu código =(")

            i = 1
            for code, result in code_interpreter:
                msg = (
                    "**Executando o código:**\n"
                    "```py\n"
                    f"{code}"
                    "```"
                    "**Resultado:**"
                    "```\n"
                    f"{result}"
                )
                msg += "```" if i == len(code_interpreter) else "```⠀"
                
                await message.channel.send(msg)
                i += 1