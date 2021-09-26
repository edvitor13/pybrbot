from ..active_record import ActiveRecord
from src.PyBrBot.config import Config

class Fields(ActiveRecord):
    
    def __init__(self):
        super().__init__(Config.get("database_pydoc"), "fields")
