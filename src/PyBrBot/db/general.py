from .active_record import ActiveRecord

class General(ActiveRecord):
    
    def __init__(self, db:str, table:str):
        super().__init__(db, table)
