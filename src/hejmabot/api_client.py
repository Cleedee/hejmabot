import httpx


class EstoqueAPI:
    def __init__(self, base_url: str = "http://localhost:8081"):
        self.base_url = base_url

    async def listar_itens(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/itens/")
            response.raise_for_status()
            return response.json()

    async def adicionar_item(self, item_dict: dict):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/itens/", json=item_dict)
            response.raise_for_status()
            return response.json()
