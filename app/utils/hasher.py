from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:
    """
    A utility class for handling password hashing and verification.

    Uses bcrypt for hashing passwords.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plaintext password using bcrypt.

        Args:
            password (str): The plaintext password to hash.

        Returns:
            str: The hashed password.
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify if the given plaintext password matches the hashed password.

        Args:
            password (str): The plaintext password to check.
            hashed_password (str): The previously hashed password to compare against.

        Returns:
            bool: True if the password matches the hashed password, False otherwise.
        """
        return pwd_context.verify(password, hashed_password)
