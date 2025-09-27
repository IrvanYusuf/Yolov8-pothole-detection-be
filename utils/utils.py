import random
import string
from lib.password_hash import Hasher
from fastapi import HTTPException, status
import uuid


def generate_password(length: int = 8):
    characters = string.ascii_uppercase + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))

    # Hashing the password
    hash = Hasher.get_password_hash(password)

    return password, hash


def check_valid_uuid(id):
    try:
        return uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={
                            "message": "Invalid UUID format"})
