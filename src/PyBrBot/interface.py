from io import StringIO
import discord as ds
from discord.embeds import Embed
from discord.utils import get
from .functions import Functions
from .tools import AsyncFast, BotLoading

"""
Classe responsável por intermediar as funcionalidades
de PyBrBot.Functions com Bot e Commands
"""
class Interface:

    bot:ds.Client = None

    # Carrega a instância de Bot para Interface
    @staticmethod
    def load_bot(bot:ds.Client) -> None:
        Interface.bot = bot


    # Atualizando status, caso diferente
    @staticmethod
    async def change_status(
        status_message:str=None
    ) -> None:
        if (status_message is None):
            status_message = await AsyncFast.to_async(
                Functions.get_status
            )

        activity = ds.Game(name=status_message)
        await Interface.bot.change_presence(activity=activity)


    # Adiciona reações com base na mensagem
    @staticmethod
    async def automatic_reaction_emojis(
        message:ds.Message, only_guild:bool=True
    ) -> None:
        # Verificar se aceitará mensagens diretas ao bot
        if (message.guild is None and only_guild):
            return None

        # Caso o autor da mensagem não seja um bot
        if (not message.author.bot):
            # Armazena as reações com base na mensagem
            reactions = await AsyncFast.to_async(
                Functions.automatic_reaction_emojis, message.content
            )
            # Adiciona cada reação
            for reaction in reactions:
                add_reaction = get(Interface.bot.emojis, name=reaction)
                await message.add_reaction(emoji=add_reaction)

    
    # Interpreta código Python da mensagem
    @staticmethod
    async def code_interpreter(
        message:ds.Message, only_guild:bool=True, only_result:bool=True
    ) -> None:
        # Verificar se aceitará mensagens diretas ao bot
        if (message.guild is None and only_guild):
            return None
        
        # Condições para iniciar
        bot_mentioned = Interface.bot.user.mentioned_in(message)
        contain_pycode = "```py" in message.content
        is_bot = message.author.bot

        if not (bot_mentioned and contain_pycode and not is_bot):
            return None
        
        # Loading
        loading = BotLoading(message).reaction()

        # Interpretando o código py da msg
        code_interpreter = []
        try:
            # Em no máximo 30 segundos
            code_interpreter = await AsyncFast.to_async_timeout(
                30, Functions.code_interpreter, message.content
            )
        except:
            await message.reply(
                "Não foi possível executar seu código =("
            )

        # Fim loading
        await loading.close()

        # Mostrando resultado
        i = 1
        for code, result in code_interpreter:
            # Caso resultado esteja vazio
            if (len(result.strip()) < 1):
                result = (
                    "Seu código não possui nenhum " 
                    "'print' com conteúdo para ser exibido =("
                )
            
            # Mensagem com o código executado
            msg_exec = f"**Executando o código:**\n```py\n{code}```"

            # Mensagem com o resultado
            msg_result = f"**Resultado:**```\n{result}"
            msg_result += "```" if i == len(code_interpreter) else "```⠀"

            # Mensagem final
            msg = msg_exec + msg_result
            
            # Verificando se mensagem não passa do limite de chars.
            if (len(msg) < 2000):
                if (not only_result):
                    await message.reply(msg, mention_author=False)
                else:
                    await message.reply(msg_result, mention_author=False)
            else:
                # Código
                if (not only_result):
                    if (len(msg_exec) <= 2000):
                        await message.reply(msg_exec, mention_author=False)
                    else:
                        # Enviando arquivo com código
                        code_file = StringIO(code)
                        await message.reply(
                            f'**Executando o código:**', 
                            file=ds.File(code_file, "CodigoExecutado.py"),
                            mention_author=False
                        )
                        code_file.close()

                # Resultado
                if (len(msg_result) <= 2000):
                    await message.reply(msg_result, mention_author=False)
                else:
                    # Enviando arquivo com resultado
                    result_file = StringIO(result)
                    await message.reply(
                        f'**Resultado:**', 
                        file=ds.File(result_file, "Resultado.txt"),
                        mention_author=False
                    )
                    result_file.close()
            i += 1

    
    # Exibe informações da documentação
    # via busca por texto
    @staticmethod
    async def search_pydoc(
        messageable:ds.abc.Messageable, search:str=""
    ) -> None:
        if (len(search.strip()) < 1):
            await messageable.send(
                f"```\nInforme algo que deseja buscar"
                "\nExemplo: .py doc print```")
            return None

        try:
            # Em no máximo 10 segundos
            embed_data = await AsyncFast.to_async_timeout(
                10, Functions.search_pydoc, search)
        except:
            await messageable.send(
                f"```\nNão foi possível procurar \"{search}\" =(\n```")

        if (len(embed_data) == 0):
            await messageable.send(
                f"```\nNenhum resultado para \"{search}\" =(\n```")
            return None
        
        await messageable.send(embed=Embed.from_dict(embed_data))


    # Envia mensagem direta de boas vindas
    # aos novos membros
    @staticmethod
    async def welcome_dm_message(member:ds.Member):
        try:
            embed_data = await AsyncFast.to_async(
                Functions.welcome_dm_message
            )
            # Adicionando menção caso aja
            embed_data["description"] = embed_data["description"].replace(
                "%mentioned%", f"<@{member.id}>"
            )
        except Exception as e:
            print("[ERR welcome_dm_message]", e)
            embed_data = {}
        
        if (len(embed_data) > 0):
            embed = Embed.from_dict(embed_data)
            try:
                await member.send("", embed=embed)
            except Exception as e:
                print("[ERR welcome_dm_message] ->",
                "Envio de Mensagens Diretas Bloqueado - ",
                f"Membro: {member.id} {member.display_name}")