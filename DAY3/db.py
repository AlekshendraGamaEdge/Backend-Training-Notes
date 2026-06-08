import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

_users_db: Dict[str, Dict[str,Any]]= {}


async def create_users(email: str, hashed_password: str, full_name: str) -> Dict[str,Any]:
    await asyncio.sleep(0.1)
    user_data = {
        "email": email,
        "hashed_password": hashed_password,
        "full_name": full_name,
        "created_at": datetime.utcnow().isoformat(),
    }
    _users_db[email] = user_data
    return user_data


async def async_find_user(email: str) -> Optional[Dict[str, Any]]:
    await asyncio.sleep(0.01)  # simulate DB read
    return _users_db.get(email)