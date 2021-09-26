from ..active_record import ActiveRecord
from src.PyBrBot.config import Config

class Docs(ActiveRecord):
    
    def __init__(self):
        super().__init__(Config.get("database_pydoc"), "docs")


    def search(self, search:str="", limit=6, offset=0):
        columns = [
            "d2.title AS parent_title", "d2.url AS parent_url", 
            "d1.id", "d1.title", "d1.original_title", "d1.description",
            "d1.url", "d1.color", "d1.visible", "d1.revised", "d1.timestamp"
        ]

        _from = """docs AS d1
        LEFT JOIN 
            docs AS d2 
            ON d1.parent_id = d2.id
        """

        where = """(
            nr(d1.title) LIKE nr(?) OR 
            nr(d1.original_title) LIKE nr(?)
        ) AND d1.visible = 1
        """

        order_by = """CASE
            WHEN d1.revised > 0 THEN 1
            WHEN nr(d1.original_title) LIKE nr(?) THEN 2
            WHEN nr(d1.title) LIKE nr(?) THEN 3
            WHEN nr(d1.title) LIKE nr(?) THEN 4
            WHEN nr(d1.original_title) LIKE nr(?) THEN 5
            ELSE 6
        END
        """

        data = self.replace_mask({"[S]":search}, [
            '%[S]%', '%[S]%', 'class [S]%', 
            '`[S]`%', '[S]%', '[S]%'
        ])
        
        return self.select(
            columns, where, order_by, data, limit, offset, _from)
