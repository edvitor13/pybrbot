import random
import re
import requests
import html
from .config import Config
from .db.pydoc import Docs, Fields
from .db.pybrbot import CodeInterpreterHistoric

"""
Classe responsável pelas funcionalidades do BOT
sem a necessidade de contato direto com a API
discord.py
"""
class Functions:
    
    # Retorna o status configurado para o BOT
    @staticmethod
    def get_status():
        return Config.get('status')

    # Retorna as reações com base na mensagem
    @staticmethod
    def automatic_reaction_emojis(message:str, shuffle=True) -> list:
        # Preparando mensagem para as buscas
        message = message.lower()
        words = message.replace("\n", " ").split(" ")

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
    @staticmethod
    def code_interpreter(message:str, merge:bool=True) -> list:
        
        # 1. Tag responsável por informar os códigos
        # que devem ser ignorados: @ignorar:1,3
        ignored_numbers = []
        if ("@ignorar:" in message):
            # Verificando se existe a tag na mensagem
            regex = r"@ignorar:([0-9,]*)|@ignorar:([0-9]*)"
            matches = re.finditer(regex, message, re.MULTILINE | re.IGNORECASE | re.DOTALL)

            # Números dos códigos que serão ignorados
            ignored_numbers = [numbers.split(",") for match in matches 
                for numbers in match.groups() if numbers != None]

            # Caso tenha obtido algum resultado
            if (len(ignored_numbers) > 0):
                ignored_numbers = [int(number.strip()) for number 
                    in ignored_numbers[0] if number.strip() != '']
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


    # Verificar se já existe uma mensagem respondida
    # em determinado servidor
    # Retorna o id da mensagem de resposta
    @staticmethod
    def _code_interpreter_reply(
        guild_id:int, message_id:int
    ) -> int:
        with CodeInterpreterHistoric() as cih:
            cih_select = cih.get(
                ["reply_id"], where="guild_id = ? and message_id = ?", 
                data=[guild_id, message_id]
            )
            data = cih.last_result

            if (not cih_select):
                print("[ERR]", cih.last_exception)
                return None
            else:
                return int(data["reply_id"])
    

    # Registra no histórico uma mensagem respondia
    # pelo Bot com o código interpretado
    @staticmethod
    def _code_interpreter_add_historic(
        guild_id:int, message_id:int, reply_id:int
    ) -> int:
        with CodeInterpreterHistoric() as cih:
            with cih.transaction():
                cih_insert = cih.insert({
                    "guild_id": guild_id,
                    "message_id": message_id,
                    "reply_id": reply_id
                })

                lastid = cih.last_result

                if (not cih_insert):
                    print("[ERR]", cih.last_exception)
                    return None
                else:
                    return int(lastid)


    # Realiza busca no banco de dados local
    # com a documentação python adptada para MarkDown
    @staticmethod
    def search_pydoc(
        search:str, limit:int=6
    ) -> dict:
        # 1. Realizando busca
        with Docs() as do:
            docs_search = do.search(search, limit)
            docs = do.last_result
            
            # Caso não tenha nenhum resultado
            if (not docs_search or len(docs) < 1):
                return {}
        
        # 2. Estrutura dos dados de retorno
        # fields[]: {"name": "", "value": "", "inline": False}
        # author: { "name": "", "url": "" }
        # "color": 2397395, # azul
        embed_data = {
            "title": "",
            "description": "",
            "url": "",
            "fields": []
        }

        # Remove trechos bagunçados dos textos
        def remove_trash(text:str):
            # Espaços após quebra de linha
            text = re.sub(r'\n +', '\n', text)
            # Informação bugada de tabela
            text = re.sub(r'\|.*?\n', '', text)
            # 3+ quebras de linha seguidas
            text = re.sub(r'\n\n\n+', '', text)

            return text

        # 3. Percorrendo resultados
        sec_result_content = ""
        for i, doc in enumerate(docs):
            # Resultado Principal
            is_first_occurrence = (i == 0)
            
            if (is_first_occurrence):
                # 3.1. Adicionando "Author"
                # Nome
                if (doc['parent_title'] is not None):
                    if ("author" not in embed_data):
                        embed_data["author"] = {}
                    embed_data["author"]["name"] = doc['parent_title']
                
                # Url
                if (doc['parent_url'] is not None):
                    if ("author" not in embed_data):
                        embed_data["author"] = {}
                    embed_data["author"]["url"] = doc['parent_url']

                # 3.2. 
                # Título
                embed_data['title'] = Functions._limit_text(
                    doc['title'], 250
                )
                # Descrição
                embed_data['description'] = Functions._limit_text(
                    remove_trash(doc['description']), 650, 
                    re_secure_zones="```.*?```|\[.*?\]\(.*?\)|`.*?`|\*\*.*?\*\*|\*.*?\*"
                )
                # Url
                embed_data['url'] = doc['url']
                
                # 3.3. Selecionando Fields
                with Fields() as fi:
                    fields_select = fi.select(
                        ["name", "value", "inline"],
                        where="doc_id = ? AND visible = 1",
                        data=[doc['id']]
                    )

                    fields = [] if not fields_select else fi.last_result
                
                for field in fields:
                    embed_data['fields'].append({
                        "name": field['name'],
                        "value": field['value'],
                        "inline": (field['inline'] == 1)
                    })
                
                continue
            
            # 3.4. Resultados Secundários
            # Serão linkados em um field adicional
            if (doc['url'] is not None):
                title = doc['title'].split("—", 1)[0].strip()
                title = title.split("(", 1)[0].strip().replace('`', '')
                title = Functions._limit_text(
                    title.split("\n", 1)[0], 30, trunc_space=False
                )
                sec_result_content += f"• [{title}]({doc['url']}) "

        # Criando e adicionando field "Ver mais"
        if (len(sec_result_content.strip()) > 0):
            embed_data['fields'].append({
                "name": "⠀",
                "value": "> " + sec_result_content[1:].strip(),
                "inline": False
            })
        
        return embed_data
    
    
    # Retorna os dados do
    # embed da mensagem de boas vindas
    @staticmethod
    def welcome_dm_message():
        return Config.get("welcome_embed")


    # Limita tamanho do texto
    @staticmethod
    def _limit_text(
        text:str, limit:int, 
        placeholder:str="...", 
        trunc_space:bool=True, 
        re_secure_zones:str=None
    ) -> str:

        if (len(text) <= limit):
            return text

        limit = limit - len(placeholder)

        # Redefinindo limites com zonas seguras
        if (re_secure_zones is not None):
            recomp = re.compile(re_secure_zones, 
                re.MULTILINE | re.IGNORECASE | re.DOTALL)

            for match in recomp.finditer(text):
                s = match.start()
                e = match.end()
                # Caso o limite esteja em zonas seguras
                if (s <= limit <= e):
                    # O limite passa a ser o valor mais próximo
                    limit = s if abs(limit - s) < abs(limit - e) else e
                    break

        # Truncando texto e invertendo
        text = text[:limit][::-1]

        # Verificando se existe um espaçamento próximo
        # para uma limitação sem corte de palavras
        if (trunc_space and re_secure_zones is None):
            next_space = text.find(" ")
            next_break = text.find("\n")
            next_valid = 0 if next_space < 0 else next_space
            if (next_break >= 0 and next_break < next_valid):
                next_valid = next_break
                
            # Adicionando placeholder
            return text[next_valid + 1:][::-1].strip() + placeholder

        return text[::-1].strip() + placeholder
