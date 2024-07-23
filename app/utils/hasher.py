from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plaintext password using bcrypt.
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify if the given plaintext password matches the hashed password.
        """
        return pwd_context.verify(password, hashed_password)
