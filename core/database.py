# Arquivo: anhanga/core/database.py
import json
import os
from datetime import datetime

DB_FILE = "investigation_current.json"

class CaseManager:
    def __init__(self):
        self.db_file = DB_FILE
        self._load_db()

    def _load_db(self):
        """Carrega ou cria o banco de dados da investigação"""
        if not os.path.exists(self.db_file):
            self.data = {
                "meta": {
                    "start_time": str(datetime.now()),
                    "status": "OPEN"
                },
                "entities": [],  # Pessoas/Empresas (Laranjas)
                "infra": [],     # Sites/IPs
                "relations": []  # Conexões (Quem mandou dinheiro pra quem)
            }
            self._save_db()
        else:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

    def _save_db(self):
        """Persiste os dados no disco"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def add_entity(self, name, doc, role="suspect"):
        """Adiciona uma Pessoa/Empresa e evita duplicatas"""
        # Verifica se já existe
        for ent in self.data["entities"]:
            if ent["document"] == doc:
                return False
        
        self.data["entities"].append({
            "name": name,
            "document": doc,
            "role": role,
            "timestamp": str(datetime.now())
        })
        self._save_db()
        return True

    def add_infra(self, domain, ip="Pending", extra_info=""):
        """Adiciona um Site/IP"""
        for inf in self.data["infra"]:
            if inf["domain"] == domain:
                return False
                
        self.data["infra"].append({
            "domain": domain,
            "ip": ip,
            "info": extra_info,
            "timestamp": str(datetime.now())
        })
        self._save_db()
        return True

    def add_relation(self, source, target, type_rel):
        """Registra uma conexão (Aresta do Grafo)"""
        self.data["relations"].append({
            "source": source,
            "target": target,
            "type": type_rel
        })
        self._save_db()

    def get_full_case(self):
        return self.data

    def nuke(self):
        """Limpa a investigação atual (Começar do zero)"""
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
            self._load_db()