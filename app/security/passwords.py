from pwdlib import PasswordHash

hasher = PasswordHash.recommended()


class PasswordManager:
    @staticmethod
    def create_hash_password(password: str) -> str:
        """принимает пароль и возращает хеш"""
        return hasher.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """сравниваем обычный пароль с хешированным паролем из бд"""
        return hasher.verify_hash(plain_password, hashed_password)


password_manager = PasswordManager()
