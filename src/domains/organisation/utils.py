import hashlib
from uuid import uuid4

class OrganisationUtils:
    def __init__(self):
        ...

    def generate_invite_code(self):
        ivt_code_str = str(uuid4().int)
        return hashlib.md5(ivt_code_str.encode()).hexdigest()