class PixForensics:
    def __init__(self, raw_payload):
        # Remove espaços em branco e aspas que o terminal possa ter adicionado
        self.raw_payload = raw_payload.strip().strip("'").strip('"')
        self.parsed_data = {}

    def parse_tlv(self, data):
        """Lê a estrutura Tag-Length-Value padrão EMV."""
        i = 0
        result = {}
        while i < len(data):
            # 1. Lê o ID (Tag) - 2 chars
            tag_id = data[i:i+2]
            i += 2
            
            # 2. Lê o Tamanho (Length) - 2 chars
            try:
                length_str = data[i:i+2]
                if not length_str: break # Fim da string
                length = int(length_str)
            except ValueError:
                break 
            
            i += 2  # <--- A CORREÇÃO ESTÁ AQUI: Faltava pular os dígitos de tamanho!
            
            # 3. Lê o Valor (Value) - 'length' chars
            value = data[i:i+length]
            i += length
            
            result[tag_id] = value
        return result

    def analyze(self):
        """Executa a extração de inteligência"""
        # Parse inicial da string completa
        root_data = self.parse_tlv(self.raw_payload)
        
        intelligence = {
            "merchant_name": root_data.get("59", "DESCONHECIDO"),
            "merchant_city": root_data.get("60", "DESCONHECIDO"),
            "txid": "***", 
            "pix_key": "*** NÃO ENCONTRADA ***"
        }

        # Engenharia Reversa do ID 26 (Merchant Account Information)
        if "26" in root_data:
            merchant_account_info = root_data["26"]
            # O ID 26 também é uma estrutura TLV aninhada
            nested_data = self.parse_tlv(merchant_account_info)
            
            if "01" in nested_data:
                intelligence["pix_key"] = nested_data["01"]
            else:
                # Fallback: Se não houver sub-ID explícito, tenta limpar a GUI
                clean_key = merchant_account_info.replace("0014br.gov.bcb.pix", "")
                intelligence["pix_key"] = clean_key

        # Extração do TxID (ID 62 -> SubID 05)
        if "62" in root_data:
            additional_data = self.parse_tlv(root_data["62"])
            if "05" in additional_data:
                intelligence["txid"] = additional_data["05"]

        self.parsed_data = intelligence
        return intelligence