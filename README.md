# PyBr BOT - Python Brasil 🐍

BOT oficial do Servidor "Python Brasil 🐍" no Discord. https://discord.gg/HbZFA8PTMW

Em caso de dúvidas entrar em contato através do canal de texto "🆘╎dúvidas" de nosso servidor.



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



###### Dependências Principais

- discord.py==1.7.3
  - pip install discord.py
- requests==2.26.0
  - pip install requests



###### Configuração

- O arquivo "**config_model.json**" deve ser renomeado para "**config.json**" e suas configurações devem ser ajustadas de acordo com o seu BOT.

- Na configuração "**token**" deve ser informado o token do BOT gerado em sua aplicação Discord: https://discord.com/developers/applications

- Caso tenha um BOT exclusivo para testes, preencha a configuração "**test_token**" também.

- "**status**" representa o status mostrado pelo BOT. 
  - Ex: Jogando **status**

- "**py_execute_code_api_url**" deve ser informada a URL da API responsável por executar os códigos Python enviados para o bot.
- "**py_execute_code_api_data**" deve ser informado os dados base que serão enviados via POST para a URL da API,  seguindo o formado chave:valor. Sendo que o valor responsável por representar o código que será executado, deve ser obrigatoriamente **"%code%"**.
  - Ex: {"key1":"valor1", "key2":"valor2" ... "key_code":"%code%"}
- "**automatic_reaction_emojis**" deve ser informada uma lista contendo as palavras-chave e seus respectivos emojis para que o BOT reaja da forma correta nas mensagens de forma automática.
  - Ex 1: caso queira que o BOT reaja com o emoji PLANTA quando alguém escrever as palavras "natureza", "planta", basta configurar:
    - [ [ ["natureza", "planta"],  ["PLANTA"] ] ]
  - Ex 2: caso queira que reaja aleatoriamente entre vários emojis.
    - [ [ ["natureza", "planta"],  ["PLANTA", "ARVORE", "NATUREZA"] ] ]
  - Ex 3: caso queira que reaja algo contido na mensagem, e não especificamente a palavras, basta adicionar um espaço:
    - [ [ ["natureza", "planta doida", "siteplanta. "],  ["PLANTA", "ARVORE", "NATUREZA"] ] ]
  - Caso sejam emojis exclusivos do servidor, ele devem ter sido enviados previamente e ter o mesmo nome.
    - [ [ ["natureza"],  ["PLANTA"] ], [ ["arvore"],  ["ARVORE"] ], ... ]



###### **Organização**

O BOT está organizado em 4 classes principais:

1. "**PyBrBot**" em "**main.py**"
   - Responsável pela execução e funcionamento do BOT: "**discord.Client**". 
2. "**Interface**" em "**src.PyBrBot.interface**"
   - Responsável por intermediar de forma assíncrona as funcionalidades síncronas de **Functions** com o **PyBrBot**.
3. "**Functions**" em "**src.PyBrBot.functions**"
   - Responsável pelas funcionalidades personalizadas do BOT. Seria o equivalente ao "back end" do BOT, não têm interação direta com ele.
4. "**Config**" em "**src.PyBrBot.config**"
   - Responsável por Carregar e Acessar as configurações do arquivo "**config.json**".

