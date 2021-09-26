from ..active_record import ActiveRecord
from src.PyBrBot.config import Config

class CodeInterpreterHistoric(ActiveRecord):
    
    def __init__(self):
        super().__init__(Config.get("database_pybrbot"), "code_interpreter_historic")
