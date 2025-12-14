# Arquivo: anhanga/modules/infra/hunter.py
import mmh3
import requests
import codecs
import urllib3
import shodan

# Desabilita avisos de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class InfraHunter:
    def __init__(self, url):
        self.url = url
        if not self.url.startswith("http"):
            self.url = f"http://{self.url}"
            
    def get_favicon_hash(self):
        """
        Baixa o favicon e calcula o MurmurHash3 para pivotar no Shodan.
        """
        target_icon = f"{self.url.rstrip('/')}/favicon.ico"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(target_icon, headers=headers, verify=False, timeout=10)
            
            if response.status_code == 200:
                # O Shodan exige Base64 com quebras de linha inseridas (padrão codecs)
                favicon_base64 = codecs.encode(response.content, 'base64')
                
                # Cálculo com a biblioteca mmh3 nativa que você instalou
                hash_val = mmh3.hash(favicon_base64)
                
                query_url = f"https://www.shodan.io/search?query=http.favicon.hash%3A{hash_val}"
                
                return hash_val, query_url
            else:
                return None, None
                
        except Exception as e:
            return None, None
        
class ShodanIntel:
    def __init__(self, api_key):
        self.api = shodan.Shodan(api_key)

    def search_by_hash(self, favicon_hash):
        """
        Consulta a API do Shodan buscando servidores com esse Favicon.
        Retorna uma lista resumida de IPs e Portas.
        """
        try:
            query = f"http.favicon.hash:{favicon_hash}"
            # Limite de 5 resultados para não estourar a cota grátis/tempo
            results = self.api.search(query, limit=5)
            
            servers = []
            for match in results['matches']:
                server_info = {
                    "ip": match['ip_str'],
                    "org": match.get('org', 'n/a'),
                    "portas": match.get('port', []),
                    "pais": match.get('location', {}).get('country_name', 'n/a'),
                    "vulns": list(match.get('vulns', {}).keys()) if 'vulns' in match else []
                }
                servers.append(server_info)
            
            return servers
        except shodan.APIError as e:
            return {"erro": str(e)}
        except Exception as e:
            return {"erro": f"Erro técnico: {e}"}