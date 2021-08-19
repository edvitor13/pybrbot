# PyBr BOT - Python Brasil 🐍

#### v1.0.0

Caso tenha alguma dúvida, entre em contato através do canal de texto `🆘╎dúvidas` de nosso servidor.

BOT oficial do Servidor "Python Brasil 🐍" no Discord. https://discord.gg/HbZFA8PTMW



###### Última versão estável:

```
git clone --branch v1.0.0 https://github.com/edvitor13/pybrbot
```



###### Funções do BOT

1. **Reação Automática**
   - Sempre que uma mensagem é enviada, reage automaticamente com base em palavras ou trechos de mensagens pré-configuradas.
      - **Interface**.automatic_reaction_emojis
      - **Config**.get("automatic_reaction_emojis")
   
2. **Execução de Código Python**
   - Sempre que uma mensagem é enviada contendo algum trecho de código Python entre as tags \```py \```, e o BOT é mencionado na mesma mensagem, ele responde enviando a execução do código.
      - **Interface**.code_interpreter
      - **Config**.get("py_execute_code_api_url")
      - **Config**.get("py_execute_code_api_data")

3. **Envia mensagem de boas vindas**
   - Sempre que um novo membro entra no servidor, envia uma mensagem direta de boas vindas pré-configurada.
      - **Interface**.welcome_dm_message
      - **Config**.get("welcome_embed")

4. **Comandos via Prefixo** `.py`
   
   - Função "**doc**"
      Retorna via busca o conteúdo da documentação PT-BR do [Python 3](https://docs.python.org/pt-br/3/).
      
      - Sintaxe: **.py doc *args**
      
      - Exemplo: 
      
        ```
        .py doc Funções Embutidas
        ```
      
      Caso a busca contenha apenas uma palavra (ou não contenha espaços), o `doc` pode ser omitido.
      - Exemplos: 
      
        ```
        .py asyncio.task
        ```
      
        ```
        .py decorador
        ```
      
        
        

###### **Principais Modificações**

- Suporte para Comandos via prefixo (agora ele herda "commands.Bot" em vez de "discord.Client").
- Classe principal "**PyBrBot**" de "**main.py**" renomeada para "**Bot**" e movida para "**src.PyBrBot.bot**".
- Criada a Classe "**Commands**" para gerenciar os comandos.
- Criada a pasta "media", para armazenar arquivos de mídia do BOT.
- Criada a pasta "databases", responsável por armazenar qualquer banco de dados que será utilizado pelo BOT.
   - **pydoc_ptbr.db** contém várias partes da documentação PT-BR do Python 3. Todos os dados foram convertidos de HTML para o formato Markdown que é suportado pelo Discord.
- Criadas as configurações: 
  - "**bot_commands_prefix**", "**test_bot_commands_prefix**", "**loading_icon**", "**loading_emoji**", "**database_pydoc**" e "**welcome_embed**".



###### Configuração

O arquivo "**config_model.json**" deve ser renomeado para "**config.json**" e suas configurações devem ser ajustadas de acordo com o seu BOT.

- Em "**token**" deve ser informado o token do BOT gerado em sua aplicação Discord: https://discord.com/developers/applications
- Em "**test_token**" caso tenha um BOT exclusivo para testes, preencha a configuração.
- "**status**" representa o status mostrado pelo BOT. 
  - Ex: Jogando **status**
- "**bot_commands_prefix**" uma lista de prefixos para que o BOT execute seus comandos (Recomendado utilizar prefixos diferentes de BOTs presentes no servidor).
  - Ex: [".py ", "."]
- "**test_bot_commands_prefix**" lista de prefixos para o BOT de Testes.
- "**loading_icon**" arquivo de imagem padrão para mensagens de loading (de preferência  GIF).
- "**loading_emoji**" nome do emoji padrão para reações de loading (de preferência emoji animado).
- "**database_pydoc**" banco de dados sqlite que será utilizado para acessar as informações de documentação do Python 3.
- "**py_execute_code_api_url**" deve ser informada a URL da API responsável por executar os códigos Python enviados para o bot.
- "**py_execute_code_api_data**" deve ser informado os dados base que serão enviados via POST para a URL da API,  seguindo o formado chave:valor. Sendo que o valor responsável por representar o código que será executado, deve ser obrigatoriamente **"%code%"**.
  - Ex: {"key1":"valor1", "key2":"valor2" ... "key_code":"%code%"}
- "**welcome_embed**" dicionário com informações do [Embed](https://discordpy.readthedocs.io/en/stable/api.html?highlight=embed#discord.Embed) que será enviado diretamente ao novo membro do servidor. 
- "**automatic_reaction_emojis**" deve ser informada uma lista contendo as palavras-chave e seus respectivos emojis para que o BOT reaja da forma correta nas mensagens de forma automática.
  - Ex 1: caso queira que o BOT reaja com o emoji PLANTA quando alguém escrever as palavras "natureza", "planta", basta configurar:
    - [ [ ["natureza", "planta"],  ["PLANTA"] ] ]
  - Ex 2: caso queira que reaja aleatoriamente entre vários emojis.
    - [ [ ["natureza", "planta"],  ["PLANTA", "ARVORE", "NATUREZA"] ] ]



###### **Organização**

> O BOT está estruturado em 5 classes principais:

1. "**Bot**" em "**src.PyBrBot.bot**"
   - Responsável pela execução e funcionamento do BOT: "**commands.Bot**". 
2. "**Commands**" em "**src.PyBrBot.commands**"
   - Responsável pelo gerenciamento dos comandos do BOT.
   - Todas as funções de comando estão contidas no método: "**_commands**".
3. "**Interface**" em "**src.PyBrBot.interface**"
   - Responsável por intermediar de forma assíncrona as funcionalidades síncronas de **Functions** com "**Bot**" e "**Commands**".
4. "**Functions**" em "**src.PyBrBot.functions**"
   - Responsável pelas funcionalidades personalizadas do BOT. Seria o equivalente ao "back end" do BOT, não têm interação direta com ele.
5. "**Config**" em "**src.PyBrBot.config**"
   - Responsável por Carregar e Acessar as configurações do arquivo "**config.json**".

> E possui um módulo auxiliar "**tools**":
> Todas as classes com prefixo `Bot` utilizam recursos de `discord.py`

1. "**AsyncFast**" em "**src.PyBrBot.tools.async_fast**"
   - Oferece funcionalidades constantemente utilizadas para ações assíncronas. 
2. "**AsyncLoop**" em "**src.PyBrBot.tools.async_loop**"
   - Permite gerar loops e loops de loops com tempo pré-configurado.
3. "**BotLoading**" em "**src.PyBrBot.tools.bot_loading**"
   - Suporte para reações/mensagens de Loading do BOT.
4. "**Database**" em "**src.PyBrBot.tools.database**"
   - Herda as funcionalidades de "**sqlite3.Connection**"
   - Oferece suporte para conexão com banco de dados sqlite. Funções exclusivas estão implementadas.



###### Dependências Principais

- discord.py==1.7.3
  - pip install discord.py
- requests==2.26.0
  - pip install requests