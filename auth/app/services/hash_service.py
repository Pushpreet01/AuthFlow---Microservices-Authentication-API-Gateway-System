from argon2 import PasswordHasher, exceptions
import hashlib

class HashService:
    # Argon2 Password Hasher
    _ph = PasswordHasher(
        time_cost=2,      # Number of iterations
        memory_cost=102400, # Memory in KB
        parallelism=8,    # Number of parallel threads
    )

    # Password hashing & verification
    @staticmethod
    def hash_password(password: str) -> str:
        return HashService._ph.hash(password)

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        try:
            return HashService._ph.verify(hashed, password)
        except exceptions.VerifyMismatchError:
            return False

    # Refresh token hashing
    @staticmethod
    def hash_refresh_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
