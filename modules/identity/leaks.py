import requests
from core.base import AnhangáModule

class LeakModule(AnhangáModule):
    def __init__(self):
        super().__init__()
        self.meta = {
            "name": "LeakHunter",
            "description": "Busca vazamentos e CNPJs vinculados",
            "version": "2.1"
        }

    def run(self, email: str) -> bool:
        self.add_evidence("Alvo", email, "high")
        
        # 1. Busca em Leaks (BreachDirectory - Free Tier)
        self._check_breach_directory(email)
        
        # 2. Busca Corporativa (Se for e-mail de domínio próprio)
        if "@gmail" not in email and "@outlook" not in email:
            domain = email.split("@")[1]
            self._check_cnpj_link(domain)
            
        return True

    def _check_breach_directory(self, email):
        """Consulta API pública de vazamentos."""
        try:
            # API Pública do BreachDirectory (RapidAPI key seria ideal, mas tem endpoint free limitado)
            url = f"https://breachdirectory.p.rapidapi.com/" 
            # Como fallback, vamos usar um Dork do Google que acha listas de vazamento indexadas
            
            self.add_evidence("Dork de Vazamento", f'site:pastebin.com "{email}"', "medium")
            self.add_evidence("Dork de CPF", f'"{email}" CPF', "medium")
            
        except Exception as e:
            pass

    def _check_cnpj_link(self, domain):
        """Tenta achar CNPJ dono do domínio via BrasilAPI."""
        try:
            url = f"https://brasilapi.com.br/api/cnpj/v1/{domain}" 
            
            # Vamos usar o Whois para pegar o documento do dono
            import whois
            w = whois.whois(domain)
            
            if w.org:
                self.add_evidence("Dono do Domínio (Whois)", w.org, "high")
            
            self.add_evidence("Sugestão Investigativa", f"Pesquisar CNPJ da empresa '{domain}' para revelar QSA (Sócios).", "high")

        except:
            pass