from __future__ import annotations
from typing import Any
import discord as ds
from discord.utils import get
from discord.ext.commands import Context
from .async_fast import AsyncFast
from .. import interface
from .. import config


"""
Envia mensagens e reações de loading 
em resposta a mensagens/comandos
"""
class BotLoading:

    def __init__(
        self, message_context:Any[ds.Message, Context]
    ):
        if (isinstance(message_context, Context)):
            self._message = message_context.message
            self._channel = message_context
        elif (isinstance(message_context, ds.Message)):
            self._message = message_context
            self._channel = message_context.channel
        
        self._closed_message = False
        self._closed_reaction = False
        self._message_loading:ds.Message = None
        self._message_reaction:ds.Message = None


    # Envia mensagem de loading
    # "start_after" a partir de quantos segundos ela será enviada
    # "stop_after" depois de enviada, em quantos segundos será removida
    def message(
        self, start_after:float=2, stop_after:float=60, text:str=""
    ) -> BotLoading:
        # Criando nova tarefa para "_loading_message"
        # não interferir na thread principal
        AsyncFast.task(
            self._loading_message, self._channel, 
            text, start_after, stop_after
        )
        return self


    # Adiciona reação de loading
    # "start_after" a partir de quantos segundos ela será adicionada
    # "stop_after" depois de adicionada, em quantos segundos será removida
    def reaction(
        self, start_after:float=0, stop_after:float=60
    ) -> BotLoading:
        # Criando nova tarefa para "_loading_reaction"
        # não interferir na thread principal
        AsyncFast.task(
            self._loading_reaction, self._message,
            start_after, stop_after
        )
        return self


    # Deleta mensagem/reação de loading
    async def close(
        self, message:bool=True, reaction:bool=True
    ) -> None:
        if (message):
            await self._close_message()
        if (reaction):
            await self._close_reaction()


    # Verifica se a mensagem de loading foi removida
    def closed_message(self) -> bool:
        return self._closed_message


    # Verifica se a reação de loading foi removida
    def closed_reaction(self) -> bool:
        return self._closed_reaction


    # Deleta mensagem de loading
    async def _close_message(self) -> bool:
        self._closed_message = True
        
        if (self._message_loading is not None):
            await self._message_loading.delete()
            self._message_loading = None
            
            return True
        
        return False


    # Limpa reações de Loading da mensagem
    async def _close_reaction(self) -> bool:
        self._closed_reaction = True
        
        if (self._message_reaction is not None):
            await self._message_reaction.clear_reaction(
                get(
                    interface.Interface.bot.emojis, 
                    name=config.Config.get("loading_emoji")
                )
            )
            self._message_reaction = None
            
            return True
        
        return False


    # Mensagem de loading com gif
    async def _loading_message(
        self, channel:ds.abc.Messageable, text:str,
        start_after:float, stop_after:float
    ) -> BotLoading:
        # Tempo de espera
        await AsyncFast.sleep(start_after)
        
        # Caso o loading já tenha sido encerrado
        if (self.closed_message()):
            return self

        # Enviando mensagem com imagem de loading
        self._message_loading = await channel.send(
            text, file=ds.File(
                config.Config.get("loading_icon"), "loading.gif"
            )
        )
        
        # Caso tenha sido determinado um tempo limite
        if (stop_after is not None):
            await AsyncFast.sleep(stop_after)
            await self._close_message()

        return self


    # Emoji animado de loading na mensagem
    async def _loading_reaction(
        self, message:ds.Message,
        start_after:float, stop_after:float
    ) -> BotLoading:
        # Tempo de espera
        await AsyncFast.sleep(start_after)

        # Caso o loading já tenha sido encerrado
        if (self.closed_reaction()):
            return self
        
        # Obtendo reação de loading
        reaction = get(
            interface.Interface.bot.emojis, 
            name=config.Config.get("loading_emoji")
        )

        # Adicionando reação
        await message.add_reaction(emoji=reaction)
        # Armazenando mensagem reagida
        self._message_reaction = message
        
        # Caso tenha sido determinado um tempo limite
        if (stop_after is not None):
            await AsyncFast.sleep(stop_after)
            await self._close_reaction()

        return self
