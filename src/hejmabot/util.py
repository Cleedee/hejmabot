from difflib import get_close_matches

from hejmabot import api_client

def refinamento_produto(nome: str):
    produtos = api_client.listar_produtos()
    nomes = [p['nome'] for p in produtos]

    matches = get_close_matches(nome, nomes, n=1, cutoff=0.3)

    if matches:
        return matches[0]
    return None
