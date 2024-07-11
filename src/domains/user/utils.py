import json
import hashlib
from datetime import datetime

from lib.redis import RedisManager
from ...config import settings

REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_PASSWORD = settings.REDIS_PASSWORD

class LoginUtils:
    def __init__(self):
        self.redis_manager = RedisManager(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD)

    def hash_pass(self, pswd: str):
        return hashlib.md5(pswd.encode()).hexdigest()

    def verify_pass(self, pass_in_db: str, pass_in_request: str):
        hashed_pass = self.hash_pass(pass_in_request)
        return pass_in_db == hashed_pass
        
    def create_session(self, user_id):
        hash_string = f"{user_id}:{datetime.now().timestamp()}"
        
        session_id = hashlib.md5(hash_string.encode()).hexdigest()
        expires_at = datetime.now().timestamp() + 3600
        expires_at_timeformatted = datetime.fromtimestamp(expires_at).strftime("%Y-%m-%d %H:%M:%S")

        self.redis_manager.set_key_with_expiry(f"user_session:{user_id}", json.dumps({"session_id": session_id, "expires_at": expires_at}), 3600)

        return session_id, expires_at_timeformatted

    def verify_session(self, user_id, session_id):
        try:
            session_detail: dict = json.loads(self.redis_manager.get_key(f"user_session:{user_id}"))
            if int(session_detail.get("expires_at")) < datetime.now().timestamp():
                return False
            
            if session_id != session_detail.get("session_id"):
                return False
            
            return True
        except Exception:
            return None