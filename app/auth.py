from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """
    Преобразовывает пароль в безопасный хеш
    """
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соотвествует ли введённый пароль сохраненному хешу
    """

    return password_hash.verify(plain_password, hashed_password)