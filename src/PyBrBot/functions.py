import random
import re
import requests
import html
from .config import Config

"""
Classe responsável pelas funcionalidades do BOT
sem a necessidade de contato direto com a API
discord.py
"""
class Functions:
    
    # Retorna o status configurado para o BOT
    def get_status(self):
        return Config.get('status')

    # Retorna as reações com base na mensagem
    def automatic_reaction_emojis(self, message:str, shuffle=True) -> list:
        # Preparando mensagem para as buscas
        message = message.lower()
        words = message.split(" ")

        # Carregando lista das configurações
        list_emojis = Config.get('automatic_reaction_emojis')
        
        # Iniciando coleta dos emojis para as reações
        final_reactions = set()
        for searches, reactions in list_emojis:
            # Para cada busca
            for search in searches:
                # Caso a busca contenha espaço
                # Verifica se está contida na mensagem
                if (" " in search and search.strip() in message):
                    final_reactions.add(random.choice(reactions))
                # Se não, verifica com base nas palavras
                elif (
                    search in words
                    or search in [word[0:-1] for word in words]
                ):
                    final_reactions.add(random.choice(reactions))

        final_reactions = list(final_reactions)

        # Se deve embaralhar a ordem dos emojis
        if (shuffle):
            random.shuffle(final_reactions)
        
        return final_reactions


    # Retorn o código python da mensagem interpretado
    def code_interpreter(self, message:str, merge:bool=True) -> list:
        
        # 1. Tag responsável por informar os códigos
        # que devem ser ignorados: @ignorar:1,3
        ignored_numbers = []
        if ("@ignorar:" in message):
            # Verificando se existe a tag na mensagem
            regex = r"@ignorar:([0-9,]*)|@ignorar:([0-9]*)"
            matches = re.finditer(regex, message, re.MULTILINE | re.IGNORECASE | re.DOTALL)

            # Números dos códigos que serão ignorados
            ignored_numbers = [
                numbers.split(",") for match in matches for numbers in match.groups() if numbers != None
            ]

            # Caso tenha obtido algum resultado
            if (len(ignored_numbers) > 0):
                ignored_numbers = [int(number.strip()) for number in ignored_numbers[0] if number.strip() != '']
            else:
                ignored_numbers = []

        # 2. Obtendo trechos de código python da mensagem
        regex = r"```py\n(.*?)```"
        matches = re.finditer(regex, message, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        # Lista de códigos
        pycodes = [code for match in matches for code in match.groups()]
        pycodes = [pycode for i, pycode in enumerate(pycodes, start=1) if i not in ignored_numbers]

        # 3. Verificar se deve mesclar todos trechos de código
        if (merge and len(pycodes) > 1 and "@interpretarSeparadamente" not in message):
            pycodes = ["\n".join(pycodes)]

        # 4. Realizando interpretação dos códigos
        interpreted_pycodes = []
        for pycode in pycodes:
            # Url da API
            api_url = Config.get('py_execute_code_api_url')
            api_data = Config.get('py_execute_code_api_data')
            api_data = {key:val.replace("%code%", pycode) for key, val in api_data.items()}

            # Coleta, filtragem e armazenamento do resultado
            try:
                request_interpret = requests.post(
                    api_url, data=api_data, timeout=10
                )

                if (request_interpret.status_code == 200):
                    interpreted_pycode = html.unescape(
                        request_interpret.text).split("<br>", 1
                    )[1]
                    interpreted_pycodes.append(interpreted_pycode)
            except:
                interpreted_pycodes.append("Falha ao interpretar código =(")
        
        # 5. Retornando resultado
        return list(zip(pycodes, interpreted_pycodes))