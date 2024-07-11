from .base_model import Base
from .table_prefixes import table_prefixes
from uuid import uuid4

NUM_DIGITS = 16

def generate_new_id(Model: Base):
    '''
    Globally generate random id for any table in the monorepo
    '''
    table_name = Model.__tablename__
    table_prefix = table_prefixes.get(table_name)
    if not table_prefix:
        return None
    

    new_id = table_prefix + "_" + str(uuid4().int)[:NUM_DIGITS] # ex: me_120676537920
    return new_id
