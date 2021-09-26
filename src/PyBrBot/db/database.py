from __future__ import annotations
import sqlite3

"""
Gerencia conexão com banco de dados
sqlite3
"""
class Database(sqlite3.Connection):
    
    def __init__(self, database:str=":memory:", **kwargs):
        super().__init__(database, **kwargs)
        
        # Modificando comportamento padrõa do retorno de dados
        self.row_factory = Database._dict_factory
        
        self.cur: sqlite3.Cursor = None

        self._create_functions()


    # Executa o cursor
    def execute(self, *args, **kwargs) -> sqlite3.Cursor:
        self.cur = self.cursor().execute(*args, **kwargs)
        return self.cur


    # Executa o commit e close
    def commit_close(self) -> None:
        self.commit()
        self.close()


    # Adiciona novas funcionalidades à conexão
    def _create_functions(self) -> Database:
        # nr -> normal_replace
        self.create_function(
            "nr", 1, Database._function_normal_replace)

        return self


    # Funcionalidade "nr"
    # Substitui todos caracteres com acentuação e especiais 
    # por sua versão base para facilitar nas buscas
    @staticmethod
    def _function_normal_replace(arg):
        replace_list = [
            (["á", "à", "â", "ã"], "a"),
            (["ó", "ô", "õ"], "o"),
            (["é", "ê"], "e"),
            (["ú", "ü"], "u"),
            (["í"], "i"),
            (["ç"], "c"),
        ]

        for replacer, replace in replace_list:
            for char in replacer:
                arg = arg.replace(char, replace)
                arg = arg.replace(char.upper(), replace.upper())

        return arg


    # Funcionalidade Factory
    # Para alterar comportamento padrão de
    # retorno de dados de (v1, v2) para {k1 -> v, k2 -> v}
    @staticmethod
    def _dict_factory(cursor:sqlite3.Cursor, row:list):
        data = {}
        for idx, col in enumerate(cursor.description):
            data[col[0]] = row[idx]
        return data
