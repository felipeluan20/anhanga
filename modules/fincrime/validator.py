# Arquivo: anhanga/modules/fincrime/validator.py
import requests
import json

class LaranjaHunter:
    def __init__(self):
        self.base_url = "https://brasilapi.com.br/api/cnpj/v1"

    def consultar_cnpj(self, cnpj_raw):
        """
        Consulta dados públicos do CNPJ na BrasilAPI para detectar anomalias (Laranjas).
        """
        # Limpa pontuação, deixa apenas números
        cnpj = "".join(filter(str.isdigit, cnpj_raw))
        
        try:
            response = requests.get(f"{self.base_url}/{cnpj}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extrai apenas o que interessa para Inteligência
                intel = {
                    "razao_social": data.get("razao_social"),
                    "nome_fantasia": data.get("nome_fantasia", "N/A"),
                    "situacao": data.get("descricao_situacao_cadastral"), # ATIVA/BAIXADA
                    "cnae_principal": data.get("cnae_fiscal_descricao"),  # A ATIVIDADE ECONOMICA (O Pulo do Gato)
                    "capital_social": data.get("capital_social"),
                    "socio_admin": data["qsa"][0]["nome_socio"] if data.get("qsa") else "N/A",
                    "risco": "DESCONHECIDO"
                }

                # Lógica Básica de Risco (Exemplo)
                # Se a atividade não for 'Jogos de azar' ou 'Tecnologia', e receber Pix de aposta... suspeito.
                keywords_suspeitas = ["PADARIA", "MERCADINHO", "BELEZA", "VESTUARIO", "CONSTRUCAO"]
                cnae = intel["cnae_principal"].upper()
                
                if any(word in cnae for word in keywords_suspeitas):
                    intel["risco"] = "ALTO (Atividade Incompatível)"
                elif "JOGOS" in cnae or "APOSTAS" in cnae:
                    intel["risco"] = "BAIXO (CNAE Correto)"
                else:
                    intel["risco"] = "MÉDIO (Analisar Manualmente)"

                return intel
            
            elif response.status_code == 404:
                return {"erro": "CNPJ não encontrado na base da Receita."}
            else:
                return {"erro": f"Erro na API: {response.status_code}"}

        except Exception as e:
            return {"erro": f"Falha de conexão: {str(e)}"}