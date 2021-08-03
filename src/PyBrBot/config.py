import json
import os

"""
Classe responsável por carregar as configurações
do arquivo config.json
"""
class Config:

    _last_modify = None
    _config = None
    
    # Carrega as configurações do arquivo config.json
    def _load(config_filename:str="config.json") -> None:
        try:
            last_modify = os.path.getmtime(config_filename)

            # Se ele foi modificado, carrega os dados
            # A armazena o último timestamp de modificação
            if (Config._last_modify != last_modify):
                Config._last_modify = last_modify
                with open(config_filename) as config_file:
                    Config._config = json.load(config_file)
        except:
            raise Exception(f"Failed to load \"{config_filename}\" configuration file.")

    # Acessa o dicionário das configurações ou uma key específica
    def get(config_name:str=None, config_filename:str="config.json") -> dict:
        Config._load()

        if (config_name is not None):
            try:
                return Config._config[config_name]
            except:
                raise Exception(f"Failed to access \"{config_name}\" configuration.")

        return Config._config