from typing import Any
from functools import partial
import asyncio


"""
Possui funcionalidades constantemente utilizadas
para gerar ou utilizar métodos assíncronos
"""
class AsyncFast:

    # Executa métodos síncronos de forma assíncrona
    @staticmethod
    async def to_async(
        function:callable, *args, **kwargs
    ) -> Any:
        loop = asyncio.get_event_loop()
       
        future = loop.run_in_executor(
            None, partial(function, *args, **kwargs)
        )
        
        return await future
    

    # Executa métodos síncronos de forma assíncrona
    # Com tempo de execução limite em segundos
    @staticmethod
    async def to_async_timeout(
        timeout:float, function:callable, *args, **kwargs
    ) -> Any:
        loop = asyncio.get_event_loop()
       
        future = loop.run_in_executor(
            None, partial(function, *args, **kwargs)
        )
       
        return await asyncio.wait_for(future, timeout, loop=loop)


    # Tempo de espera assíncrono
    @staticmethod
    async def sleep(time:float=0) -> None:
        await asyncio.sleep(time)


    # Executa a função sem interferir no loop principal
    @staticmethod
    def task(function:callable, *args, **kwargs) -> None:
        loop = asyncio.get_event_loop()
        loop.create_task(function(*args, **kwargs))
