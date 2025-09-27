import bcrypt


class Hasher():
    @staticmethod
    def verify_password(plain_password, hashed_password):
        passBytes = plain_password.encode('utf-8')
        return bcrypt.checkpw(passBytes, hashed_password)

    @staticmethod
    def get_password_hash(password):

        # converting password to array of bytes
        bytes = password.encode('utf-8')

        # generating the salt
        salt = bcrypt.gensalt()

        # Hashing the password
        hash = bcrypt.hashpw(bytes, salt)
        return hash
