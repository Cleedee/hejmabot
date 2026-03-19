import ollama
import json
import datetime

class AnalistaEconomico:
    def __init__(self, model="llama2"):
        self.model = model

    async def analisar_gastos(self, dados_consumo: list):
        if not dados_consumo:
            return "Ainda não tenho dados de consumo suficientes para analisar."

        prompt = f"""
        Você é um especialista em economia doméstica. Analise os seguintes dados de consumo da minha casa:
        {json.dumps(dados_consumo)}

        Responda em português de forma concisa:
        1. Qual categoria estamos gastando mais?
        2. Houve desperdício (itens com status 'desperdiçado')?
        3. Dê uma dica prática para economizar no próximo mês baseado nesses nomes e preços.
        """

        response = ollama.chat(model=self.model, messages=[
            {'role': 'user', 'content': prompt}
        ])
        return response['message']['content']



class ProcessadorUniversal:
    def __init__(self, model="llama3"):
        self.model = model

    async def processar_entrada(self, texto: str):
        hoje = datetime.date.today().isoformat()

        prompt = f"""
        Você é um extrator de dados de compras de alta precisão. 
        O texto abaixo pode ser uma frase única ou uma lista de itens (como do Google Keep).
        
        REGRAS:
        1. Identifique o LOCAL DA COMPRA se mencionado (ex: 'no Mercado X'). Se não houver, deixe nulo.
        2. Extraia TODOS os itens mencionados.
        3. Para cada item, estime a 'data_validade' baseada em hoje ({hoje}) se não for dita:
           - Perecíveis (carne, leite): +7 dias.
           - Mercearia (arroz, feijão): +180 dias.
        4. Converta preços para float (ex: '48 reais' -> 48.0).

        TEXTO DO USUÁRIO:
        "{texto}"

        RETORNE APENAS UM JSON NESTE FORMATO, SEM EXPLICAÇÕES:
        {{
            "local_compra": "Nome do Local ou null",
            "itens": [
                {{
                    "nome": "string",
                    "categoria": "string",
                    "quantidade_inicial": float,
                    "unidade": "string",
                    "preco_pago": float,
                    "data_validade": "YYYY-MM-DD"
                }}
            ]
        }}
        """


        response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}])
        print(response["message"]["content"])
        
        try:
            # Limpa a resposta caso a IA coloque blocos de código ```json
            conteudo = response["message"]["content"].strip()
            if "```json" in conteudo:
                conteudo = conteudo.split("```json")[1].split("```")[0]

            return json.loads(conteudo)
        except Exception as e:
            print(f"Erro ao processar IA: {e}")
            return None
