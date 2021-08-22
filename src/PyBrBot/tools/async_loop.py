from __future__ import annotations
from typing import Union
from functools import partial
import asyncio
import time


"""
Responsável pela construção 
de loops assíncronos para métodos async
"""
class AsyncLoop():
    
    def __init__(
        self, name:str="Async Loop", sleep_secs:int=60, 
        sleep_minutes:int=0, sleep_hours:int=0,
        print_out:bool=True, callback:callable=None
    ):
        self.name = name
        self.sleep = self._calc_sleep(sleep_secs, sleep_minutes, sleep_hours)
        self.callback = callback
        self.print_out = print_out
        
        self.stoped = False
        self.ignored = False

        self.functions:list[callable] = []
        self.loops:list[AsyncLoop] = []
        self.loop_count:int = None

        self._parallel:bool = None
        self._before:bool = False
        

    # Seta config _parallel global
    def parallel(self, value:bool) -> AsyncLoop:
        self._parallel = value
        return self


    # Seta config _before global
    # Se o loop deve começar antes do tempo de sleep
    def before(self, value:bool=True) -> AsyncLoop:
        self._before = value
        return self 
    

    # Adiciona Método ou AsyncLoop que será executado
    def add(
        self, function:Union[AsyncLoop, callable], *args, **kwargs
    ) -> AsyncLoop:
        if (isinstance(function, AsyncLoop)):
            self.loops.append(function)
        elif (callable(function)):
            self.functions.append(
                partial(function, *args, *kwargs)
            )
        return self


    # Recebe vários Métodos ou AsyncLoops que serão executados
    def add_all(self, *args) -> AsyncLoop:
        for arg in args:
            self.add(arg)
        return self


    # Executa todos os Métodos adicionados
    # infinitamente a cada X segundos
    async def run(self, parallel:bool=True) -> None:
        parallel = parallel if self._parallel is None else self._parallel

        if (not parallel):
            return await self._run_one_at_time()
        
        return await self._run_parallel()


    # Executa todos os AsyncLoops.run adicionados
    async def super_run(self) -> None:
        await self._super_run_parallel()
    

    # Para o loop
    def stop(self, value:bool=True) -> None:
        self.stoped = value


    # Ignora o loop
    def ignore(self, value:bool=True) -> None:
        self.ignored = value
    

    # Printador
    def _print(self, *args, **kwargs):
        if (self.print_out):
            print(*args, **kwargs)


    # Retorna o tempo em segundos
    def _calc_sleep(self, secs:int, mins:int, hours:int) -> int:
        return secs + (mins * 60) + (hours * 60 * 60)


    # Executa todos método ao mesmo tempo
    async def _run_parallel(self) -> None:
        loops = 1
        while (len(self.functions) > 0):
            self.loop_count = loops

            # Caso tenha função de callback
            if (callable(self.callback)):
                self.callback(self)

            # Caso tenha sido parado
            if (self.stoped):
                break

            # Caso tenha sido ignorado
            if (self.ignored):
                await asyncio.sleep(self.sleep)
                loops += 1
                continue

            # Espera antes de executar o código
            if (self._before):
                await asyncio.sleep(self.sleep)

            self._print(f"\n{self.name} {loops}: {time.strftime('%d/%m/%Y %H:%M:%S')}")
            
            # Gerador de métodos
            def functions_generator():
                for function in self.functions:
                    self._print(f" >>> {function.func.__name__}")
                    yield function
            
            # Executando os métodos
            try:
                await asyncio.gather(
                    *[function() for function in functions_generator()]
                )
            except Exception as e:
                self._print(f" [ERR] >>> ", end="")
                self._print(e)
            
            # Espera depois de executar o código
            if (not self._before):
                await asyncio.sleep(self.sleep)

            loops += 1


    # Executa um método de cada vez
    async def _run_one_at_time(self) -> None:
        loops = 1
        while (len(self.functions) > 0):
            self.loop_count = loops

            # Caso tenha função de callback
            if (callable(self.callback)):
                self.callback(self)

            # Caso tenha sido parado
            if (self.stoped):
                break

            # Caso tenha sido ignorado
            if (self.ignored):
                await asyncio.sleep(self.sleep)
                loops += 1
                continue
            
            # Espera antes de executar o código
            if (self._before):
                await asyncio.sleep(self.sleep)

            self._print(f"\n{self.name} {loops}: {time.strftime('%d/%m/%Y %H:%M:%S')}")

            # Executando métodos
            try:
                for function in self.functions:
                    self._print(f" >>> {function.func.__name__}")
                    await function()
            except Exception as e:
                self._print(f" [ERR] >>> ", end="")
                self._print(e)
            
            
            # Espera depois de executar o código
            if (not self._before):
                await asyncio.sleep(self.sleep)
            
            loops += 1


    # Executa todos loops ao mesmo tempo
    async def _super_run_parallel(self) -> None:
        if (len(self.loops) > 0):
            self._print(f"\n{self.name}: {time.strftime('%d/%m/%Y %H:%M:%S')}")
            
            # Gerador de run dos loops
            def loops_generator():
                for loop in self.loops:
                    self._print(f" >>> {loop.name}")
                    yield loop.run
            
            # Executando runs dos lopps
            try:
                await asyncio.gather(
                    *[loop() for loop in loops_generator()]
                )
            except Exception as e:
                self._print(f" [ERR] >>> ", end="")
                self._print(e)
