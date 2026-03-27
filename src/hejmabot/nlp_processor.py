import ollama
import json
import datetime

class Receitas:
    def __init__(self, model="llama2"):
        self.model = model

    async def sugerir_receita(self, itens_vencendo: list):
        if not itens_vencendo:
            return "Não há itens vencendo em breve. Use o que preferir do estoque!"

        ingredientes = ", ".join([p['nome'] for p in itens_vencendo])
        
        prompt = f"""
        Você é um Chef especializado em economia doméstica. 
        Tenho os seguintes ingredientes que VENCEM EM BREVE: {ingredientes}.
        
        TAREFA:
        1. Sugira UMA receita principal que use o máximo desses itens.
        2. A receita deve ser nutritiva e atraente para duas crianças (7 e 10 anos).
        3. Seja breve nos passos (máximo 5 passos).
        4. Liste ingredientes extras simples que provavelmente tenho na despensa (sal, óleo, cebola).
        
        Responda em Português.
        """

        response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']

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
                    "quantidade": float,
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


class ProcessadorCompras:
    def __init__(self, model="llama3"):
        self.model = model

    async def extrair_dados_relacionais(self, texto: str):
        hoje = datetime.date.today().isoformat()
        
        prompt = f"""
        Você é um parser de alta precisão para um sistema de inventário doméstico.
        Sua tarefa é transformar o texto do usuário em um JSON estruturado para um banco de dados relacional.

        REGRAS DE EXTRAÇÃO:
        1. LOCAL: Identifique o estabelecimento (ex: 'Mercado Extra', 'Armazém Dom Severino').
        2. PRODUTOS: Normalize os nomes (ex: 'leite condensado moça' -> 'Leite Condensado').
        3. QUANTIDADE: Extraia apenas o número. Se não houver, assuma 1.0.
        4. PREÇO: Extraia o valor total pago por aquele item (float).
        5. VALIDADE: Estime a validade a partir de hoje ({hoje}):
           - Carnes/Laticínios: +7 dias.
           - Grãos/Latas: +180 dias.
           - Limpeza: +365 dias.

        TEXTO DO USUÁRIO:
        "{texto}"

        EXEMPLO DE SAÍDA DESEJADA:
        {{
            "local_compra": "Nome do Mercado",
            "itens": [
                {{
                    "nome": "Arroz Integral",
                    "categoria": "Grãos",
                    "quantidade": 2.0,
                    "unidade": "kg",
                    "preco_pago": 15.50,
                    "data_validade": "2026-09-22"
                }}
            ]
        }}

        RETORNE APENAS O JSON:
        """

        response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}])
        
        # Limpeza simples para garantir que pegamos apenas o bloco JSON
        conteudo = response['message']['content']
        inicio = conteudo.find('{')
        fim = conteudo.rfind('}') + 1
        return json.loads(conteudo[inicio:fim])
