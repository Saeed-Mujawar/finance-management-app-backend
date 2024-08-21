from passlib.context import CryptContext

pwd_cxt = CryptContext(schemes=['bcrypt'], deprecated="auto")

class Hash:
    @staticmethod
    def bcrypt(password: str) -> str:
        try:
            return pwd_cxt.hash(password)
        except Exception as e:
            raise RuntimeError("Error hashing password.") from e
    
    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        try:
            return pwd_cxt.verify(plain_password, hashed_password)
        except Exception as e:
            raise RuntimeError("Error verifying password.") from e
