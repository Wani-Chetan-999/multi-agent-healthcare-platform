import httpx
from typing import Optional, Dict, Any

BASE_URL = "http://localhost:8000/api/v1"

class APIClient:
    @staticmethod
    def register(email: str, password: str, full_name: str) -> Dict[str, Any]:
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{BASE_URL}/auth/register",
                    json={"email": email, "password": password, "full_name": full_name}
                )
                return response.json()
        except Exception as e:
            return {"detail": f"Network transport error occurred: {str(e)}"}

    @staticmethod
    def login(email: str, password: str) -> Dict[str, Any]:
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{BASE_URL}/auth/login",
                    data={"username": email, "password": password}
                )
                return response.json()
        except Exception as e:
            return {"detail": f"Network transport error occurred: {str(e)}"}