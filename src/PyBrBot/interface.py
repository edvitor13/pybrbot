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

    # Instância carregada do BOT
    bot:ds.Client = None

    # Funções decoradoras
    
    # Responsável por executar o método caso
    # ele esteja configurado como "true" em
    # "bot_functions"
    def bot_function(method):
        def return_method(*args, **kwargs):
            if (Functions.bot_function(method)):
                return method(*args, **kwargs)
        
        return return_method


    # Carrega a instância de Bot para Interface
    @staticmethod
    def load_bot(bot:ds.Client) -> None:
        Interface.bot = bot


    # Atualizando status, caso diferente
    @staticmethod
    @bot_function
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
    @bot_function
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
                try:
                    add_reaction = get(Interface.bot.emojis, name=reaction)
                    await message.add_reaction(emoji=add_reaction)
                except Exception as e:
                    print(f"[ERR] Falha ao reagir automaticamente {add_reaction}")
                    print(e)


    # Interpreta código Python da mensagem
    @staticmethod
    @bot_function
    async def code_interpreter(
        message:ds.Message, only_guild:bool=True
    ) -> None:
        # Verificar se aceitará mensagens diretas ao bot
        if (message.guild is None and only_guild):
            return None
        
        # Condições para iniciar
        bot_mentioned = Interface.bot.user.mentioned_in(message)
        is_bot = message.author.bot

        if not (bot_mentioned and not is_bot):
            return None
        
        # Loading
        async with BotLoading(message).reaction():
            # Verificando se tem arquvios anexados
            file = {}
            if (len(message.attachments) > 0):
                file["name"] = message.attachments[0].filename
                file["url"] = message.attachments[0].url
            
            # Interpretando o código py da msg
            code_interpreter = []
            try:
                # Em no máximo 30 segundos
                code_interpreter = await AsyncFast.to_async_timeout(
                    30, Functions.code_interpreter, message.content, file)
            except Exception as e:
                print(e)
                await Interface._code_interpreter_reply(
                    message, "```Não foi possível executar seu código =(```")

        # Mostrando resultado
        i = 1
        final_msg_result = ""
        for _code in code_interpreter:
            lang = _code["lang"]
            time = _code["time"]
            result = _code["result"]
            result_images = _code["result_images"]

            # Caso resultado esteja vazio
            if (not result and not result_images):
                result = "Seu código não possui nenhum " \
                    "'print' com conteúdo para ser exibido"
            
            result = f"```\n{result}```" if result else ""

            # Mensagem com o resultado
            msg_result = f"\nResultado em **{lang}**{result}"
            
            if (not result_images):
                is_last_ci = i == len(code_interpreter)
                msg_result += "" if is_last_ci else "\n"
            else:
                msg_result += f"\n{result_images}"

            final_msg_result += msg_result

            i += 1

        # Verificando se mensagem não passa do limite de chars.
        if (len(final_msg_result) <= 2000):
            await Interface._code_interpreter_reply(message, final_msg_result)
        else:
            await Interface._code_interpreter_reply(message, 
                "```Resultado muito longo para ser exibido no discord```")

        return None


    # Responsável por enviar conteúdo de resposta
    # do método code_interpreter
    @staticmethod
    async def _code_interpreter_reply(
        message:ds.Message, *args, **kwargs
    ) -> ds.Message:

        # Verificando se já existe uma resposta para mensagem
        reply_id = await AsyncFast.to_async(
            Functions._code_interpreter_reply, message.guild.id, message.id
        )

        if (reply_id is None):
            # Adicionando resposta
            msg = await message.reply(*args, **kwargs)
            
            # Registrando histórico
            await AsyncFast.to_async(
                Functions._code_interpreter_add_historic, 
                message.guild.id, message.id, msg.id
            )
            
            return msg
        else:
            try:
                context = await Interface.bot.get_context(message)
                reply_msg = await context.fetch_message(reply_id)

                msg = await reply_msg.edit(content=args[0])

            except Exception as e:
                print("[ERR] Falha ao editar mensagem 'code_interpreter'")
                print(e)
                msg = None

            return msg

    
    # Exibe informações da documentação
    # via busca por texto
    @staticmethod
    @bot_function
    async def search_pydoc(
        messageable:ds.abc.Messageable, search:str=""
    ) -> None:
        # Caso a busca seja vazia
        if (len(search.strip()) < 1):
            await messageable.send(
                f"```\nInforme algo que deseja buscar"
                "\nExemplo: .py doc print```")
            return None
        
        # Loading
        async with BotLoading(messageable).reaction(2, 10):
            # Buscando dados
            try:
                embed_data = await AsyncFast.to_async_timeout(
                    10, Functions.search_pydoc, search)
            except:
                await messageable.send(
                    f"```\nNão foi possível procurar \"{search}\" =(\n```")

        # Caso não tenha resultado
        if (len(embed_data) == 0):
            await messageable.send(
                f"```\nNenhum resultado para \"{search}\" =(\n```")
            return None
        
        # Enviando embed com resultados
        await messageable.send(embed=Embed.from_dict(embed_data))


    # Envia mensagem direta de boas vindas
    # aos novos membros
    @staticmethod
    @bot_function
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
                print("\nMensagem de boas vindas para: ", member)
                await member.send("", embed=embed)
            except Exception as e:
                print("[ERR welcome_dm_message] ->",
                "Envio de Mensagens Diretas Bloqueado - ",
                f"Membro: {member.id} {member.display_name}")
