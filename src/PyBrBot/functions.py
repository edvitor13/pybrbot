import random
import re
import time
from typing import Union
import requests
import html
import json
import base64
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
    def code_interpreter(message:str, file:dict={}, timeout:int=15) -> list:
        extracted_code = Functions._code_interpreter_extract_codes(message)
        extracted_code = Functions._code_interpreter_load_basecode(
            extracted_code, file
        )

        results = []
        for data in extracted_code.values():
            # Api
            api_url = data["url"]
            api_data = data["data"]
            api_data = {
                k:v.replace("%code%", data["all_codes"]) 
                for k, v in api_data.items()
            }

            result = { 
                "lang": api_data["lang"],
                "result": None,
                "time": None
            }

            # Coleta, filtragem e armazenamento do resultado
            try:
                _start_time = time.time()
                
                request_interpret = requests.post(
                    api_url, data=api_data, timeout=timeout)
                
                result["time"] = time.time() - _start_time

                # Compensando o tempo de delay
                if (result["time"] > 1):
                    result["time"] -= 1

                if (request_interpret.status_code == 200):
                    interpreted_code = html.unescape(
                        request_interpret.text)

                    if ("<br>" in interpreted_code):
                        interpreted_code = interpreted_code.split("<br>")[-1]
                    
                    # Fazendo upload de imagens caso exista
                    imgbb = Functions._code_interpreter_imgbb_api_upload(
                        interpreted_code
                    )

                    result["result"] = imgbb[0]
                    result["result_images"] = imgbb[1]

            except Exception as e:
                result["result"] = "Falha ao interpretar código"

            results.append(result)

        return results


    # Faz upload de IMG HTML B64 no serviço imgbb
    # e substitui as TAGs HTML pela URL retornada
    @staticmethod
    def _code_interpreter_imgbb_api_upload(
        code_result:str
    ) -> tuple[str, str]:
        regex = r"<img *src *= *\"data:.*?base64,(.*?)\" .*?/>"

        matches = re.finditer(
            regex, code_result, re.IGNORECASE | re.DOTALL | re.MULTILINE)

        def upload_imgbb(img_base64:str) -> Union[str, bool]:
            api_url = "https://api.imgbb.com/1/upload"
            api_data = {
                "key": Config.get("imgbb_api_key"),
                "image": img_base64
            }

            upload = requests.post(
                    api_url, data=api_data, timeout=10)

            if (upload.status_code == 200):
                upload = json.loads(upload.text)

                if ("success" in upload and upload["success"]):
                    return upload["data"]["url"]

            return False

        images = ""
        count = 1
        for match in matches:
            img_html = match.group(0).strip()
            img_base64 = match.group(1).strip()
            
            img_url = upload_imgbb(img_base64)
            img_placeholder = f""

            if (img_url is False):
                img_placeholder = f"<IMG {count}: ERRO AO FAZER UPLOAD>"
            
            images += f"IMG {count}: {img_url}>\n"

            code_result = code_result.replace(
                img_html, img_placeholder)
            
            count += 1

        return code_result, images
    

    # Carrega basecodes "src/basecode"
    # de cada linguagem caso tenha sido configurado
    @staticmethod
    def _code_interpreter_load_basecode(
        extracted_code:dict, file:dict={}
    ) -> dict:
        def download_insert_file(file:dict, code:str):
            if (len(file) < 2):
                code = code.replace("%PYBRBOT_FILES%", "")
                return code

            try:
                get = requests.get(file["url"])
                b64_file = base64.b64encode(get.content).decode()
            except Exception as e:
                code = code.replace("%PYBRBOT_FILES%", "")
                return code

            if (get.status_code != 200):
                code = code.replace("%PYBRBOT_FILES%", "")
                return code
            
            b64_file_insert = f'{file["name"]}": "{b64_file}'
            code = code.replace("%PYBRBOT_FILES%", b64_file_insert)

            return code

        for flag, data in extracted_code.items():
            if ("basecode" in data):
                with open(data["basecode"], "r", encoding="utf8") as _file:
                    code = _file.read() + "\n"
                
                code = download_insert_file(file, code)

                extracted_code[flag]["codes"].insert(0, code)
                extracted_code[flag]['all_codes'] = \
                    f"{code}\n{data['all_codes']}"
        
        return extracted_code


    # Extrai os códigos da mensagem
    @staticmethod
    def _code_interpreter_extract_codes(message:str) -> dict:
        regex = r"```([a-z0-9]*)(.*?)```"

        matches = re.finditer(
            regex, message, re.IGNORECASE | re.DOTALL | re.MULTILINE)

        codes = {}
        for match in matches:
            lang = match.group(1).strip().lower()
            code = match.group(2).strip()

            if (len(lang) < 1):
                continue

            if (lang not in codes):
                codes[lang] = {}
                codes[lang]["codes"] = []
                codes[lang]["all_codes"] = ""
            
            codes[lang]["codes"].append(code)
            codes[lang]["all_codes"] += f"{code}\n\n"
        
        codes = Functions.__code_interpreter_set_langs_api(codes)

        return codes


    @staticmethod
    def __code_interpreter_set_langs_api(extracted_code:dict) -> dict:
        config = Config.get('execute_code_api')
        
        _url = config.pop("url")
        _data = config.pop("data")

        # Filtrando códigos válidos com base nas APIs
        # E inserindo informações da API
        _extracted_code = {}
        for extr_lang, extr_data in extracted_code.items():
            
            for langs, data in config.items():
                if (extr_lang in langs):
                    data["url"] = data["url"] if "url" in data else _url
                    data["data"] = {**_data, **data["data"]}

                    _extracted_code[extr_lang] = {**extr_data, **data}

        # Mesclando mesmos tipos de códigos
        # escritos de formas diferentes
        # Ex: py e python
        remove_langs = []
        for lang1, data1 in _extracted_code.items():
            
            if (lang1 in remove_langs):
                continue

            for lang2, data2 in _extracted_code.items():
                diff_lang = lang1 != lang2
                equal_api = data1["data"] == data2["data"]

                if (diff_lang and equal_api):
                    data1["codes"] += data2["codes"]
                    data1["all_codes"] += f"{data2['all_codes']}\n\n"

                    _extracted_code[lang1] = data1
                    remove_langs.append(lang2)

        # Removendo tipos que foram mesclados
        _extracted_code = {
            k:v for k,v in _extracted_code.items() if k not in remove_langs
        }

        return _extracted_code


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
