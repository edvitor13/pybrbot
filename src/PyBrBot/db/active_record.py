from __future__ import annotations
from .database import Database
from abc import ABC

"""
Responsável por adicionar funcionalidades SQL
às entidades de DB
"""
class ActiveRecord(ABC):

    def __init__(self, db_name:str, table:str):
        self.db = Database(db_name)
        self.table = table

        self.begin_transaction = False
        self.fail_transaction = False

        self.last_result = None
        self.last_exception = None
        self.last_sql = None
        self.last_transaction_is_valid = False
    

    def __enter__(self):
        return self


    def __exit__(self, *args):
        self.close()


    def replace_mask(self, masks:dict, data:list):
        for mask, value in masks.items():
            data = list(map(lambda s: s.replace(mask, value), data))
        
        return data


    def count(self, where: str="", data: list=[], _from:str=None):
        count = self.select(["COUNT(1) AS count"], where, "", data, 0, 0, _from)

        if (not count):
            self.last_result = 0
            return False
        else:
            self.last_result = self.last_result[0]["count"]
            return True


    def get(
        self, columns: list=["*"], where: str="", order_by: str="",
        data: list=[], _from:str=None
    ):
        get = self.select(columns, where, order_by, data, 1, 0, _from)

        if (not get):
            return False
        elif (len(self.last_result) < 1):
            self.last_exception = Exception("Get: Not results")
            return False
        else:
            self.last_result = self.last_result[0]
            return True


    def select(
        self, columns: list=["*"], where: str="", order_by: str="", 
        data: list=[], limit: int=100, offset: int=0, _from:str=None
    ) -> bool:
        self._reset_last()

        if (_from is None):
            _from = self.table

        columns  = ', '.join(columns)
        _from    = f"FROM {_from}"
        where    = f"WHERE {where}" if where != "" else "" 
        order_by = f"ORDER BY {order_by}" if order_by != "" else "" 
        limit    = f"LIMIT {limit}" if limit != 0 else ""
        offset   = f"OFFSET {offset}" if offset != 0 else ""
        
        sql = f"SELECT {columns} {_from} {where} {order_by} {limit} {offset}"

        self.last_sql = sql

        try:
            self.db.execute(sql, data)
            self.last_result = self.db.cur.fetchall()
            
            return True

        except Exception as e:
            self._register_fail_transaction(e)
            
            return False


    def insert(
        self, data: dict, into: str=None
    ) -> bool:
        self._reset_last()

        if (into is None):
            into = self.table

        keys   = ', '.join(data.keys())
        values = list(data.values())
        tokens = ", ".join(["?" for _ in values])

        sql = f"INSERT INTO {into}({keys}) VALUES({tokens})"

        self.last_sql = sql

        try:
            self.db.execute(sql, values)
            self.last_result = self.db.cur.lastrowid

            return True

        except Exception as e:
            self._register_fail_transaction(e)
            
            return False

    
    def multiple_inserts(
        self, data: list[dict], callback: callable=None, into: str=None
    ) -> bool:
        self._reset_last()

        if (into is None):
            into = self.table
        
        results = []
        for d in data:
            insert = self.insert(d)
            results.append(insert)

            if (callback is callable):
                callback(insert, self)
        
        return all(results)


    def update(
        self, data: dict, complement_data: list | int = [],
        where: str = "id = ?", fail_on_rows: bool=False, table: str = None
    ) -> bool:
        self._reset_last()

        if (table is None):
            table = self.table

        if (type(complement_data) is int):
            complement_data = [complement_data]
        
        where = f"WHERE {where}" if where != "" else "" 

        tokens = ", ".join([f"{d}=?" for d in data.keys()])
        values = list(data.values()) + complement_data

        sql = f"UPDATE {table} SET {tokens} {where}"

        self.last_sql = sql

        try:
            self.db.execute(sql, values)
            self.last_result = self.db.cur.rowcount

            if (fail_on_rows and self.last_result < 1):
                self._register_fail_transaction(
                    Exception("Update: No rows were affected")
                )
                return False
            
            return True

        except Exception as e:
            self._register_fail_transaction(e)

            return False


    def delete(
        self, data: list | int = [], where: str="id = ?",  
        fail_on_rows: bool=False, table: str=None
    ) -> bool:
        self._reset_last()
        
        if (table is None):
            table = self.table

        if (type(data) is int):
            data = [data]

        where = f"WHERE {where}" if where != "" else "" 

        sql = f"DELETE FROM {table} {where}"

        self.last_sql = sql

        try:
            self.db.execute(sql, data)
            self.last_result = self.db.cur.rowcount

            if (fail_on_rows and self.last_result < 1):
                self._register_fail_transaction(
                    Exception("Delete: No rows were affected")
                )
                return False
            
            return True

        except Exception as e:
            self._register_fail_transaction(e)

            return False


    def query(
        self, sql: str, data: list=[]
    ) -> bool:
        self._reset_last()

        self.last_sql = sql

        try:
            self.db.execute(sql, data)
            self.last_result = self.db.cur

            return True

        except Exception as e:
            self._register_fail_transaction(e)

            return False


    def transaction(self):
        class Transaction:
            def __init__(self, ac: ActiveRecord):
                self.ac = ac

            def __enter__(self):
                self.ac.begin()

            def __exit__(self, *args):
                self.ac.commit()

        return Transaction(self)


    def begin(self) -> ActiveRecord:
        self.begin_transaction = True
        return self


    def commit(self) -> ActiveRecord:
        if (self.begin_transaction and self.fail_transaction):
            self._reset_transaction()
            self.last_transaction_is_valid = False
        else:
            self.db.commit()
            self.last_transaction_is_valid = True

        return self
    

    def rollback(self) -> ActiveRecord:
        self.db.rollback()
        return self


    def close(self) -> ActiveRecord:
        self.db.close()
        return self


    def commit_close(self) -> ActiveRecord:
        self.commit().close()
        return self


    def _reset_last(self) -> None:
        self.last_result = None
        self.last_exception = None
        self.last_sql = None


    def _reset_transaction(self) -> None:
        self.begin_transaction = False
        self.fail_transaction = False

        self.rollback()


    def _register_fail_transaction(
        self, exception: Exception
    ) -> None:
        self.last_exception = exception

        if (self.begin_transaction):
            self.fail_transaction = True
