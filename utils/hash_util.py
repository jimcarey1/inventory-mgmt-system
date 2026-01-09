import asyncio
from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()


async def hash_password(password: str) -> str:
    return await asyncio.to_thread(password_hasher.hash, password)

async def verify_password(password: str, hash: str) -> bool:
    return await asyncio.to_thread(password_hasher.verify, password, hash)
