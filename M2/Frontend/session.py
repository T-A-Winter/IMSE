from typing import Union

from SQL_backend.models import User, Gast

class Session():
    def __init__(self, user: [Union[User, Gast]]):
        
        self.user: [Union[User, Gast]] = user   
        