# Arquivo: anhanga/modules/graph/builder.py
import networkx as nx
import matplotlib.pyplot as plt

class GraphBrain:
    def __init__(self):
        self.G = nx.Graph()

    def add_fincrime_data(self, nome_laranja, cpf_cnpj, origem="Pix"):
        """Adiciona nós financeiros"""
        # Nó Central (Pessoa) - Vermelho Neon
        self.G.add_node(nome_laranja, type='person', label=nome_laranja)
        
        # Nó do Documento - Vermelho Claro
        self.G.add_node(cpf_cnpj, type='doc', label=cpf_cnpj)
        
        # Conexão
        self.G.add_edge(nome_laranja, cpf_cnpj, relation='documento')

    def add_infra_data(self, domain, ip_real, provider="Shodan"):
        """Adiciona nós de infraestrutura"""
        # Nó do Site - Azul Neon
        self.G.add_node(domain, type='domain', label=domain)
        
        # Nó do IP - Ciano Neon
        self.G.add_node(ip_real, type='ip', label=ip_real)
        
        # Conexão
        self.G.add_edge(domain, ip_real, relation='hospedado_em')

    def connect_entities(self, entity1, entity2, relation_type="suspeita"):
        """Cria o link entre o Crime Financeiro e a Infra"""
        self.G.add_edge(entity1, entity2, relation=relation_type)

    def plot_investigation(self):
        """Gera a janela visual no estilo Cyberpunk/Dark"""
        # 1. Configura o Fundo Preto (Dark Mode)
        plt.style.use('dark_background')
        plt.figure(figsize=(12, 8)) # Janela maior
        
        # 2. Layout mais espaçado (k=0.5 empurra os nós para longe)
        pos = nx.spring_layout(self.G, seed=42, k=0.8) 
        
        # 3. Definição de Cores Neon baseada no tipo
        color_map = []
        for node in self.G.nodes:
            tipo = self.G.nodes[node].get('type')
            if tipo == 'person': 
                color_map.append('#ff3333') # Vermelho Neon
            elif tipo == 'doc': 
                color_map.append('#ff8080') # Salmão
            elif tipo == 'domain': 
                color_map.append('#3333ff') # Azul Neon
            elif tipo == 'ip': 
                color_map.append('#00ffff') # Ciano Brilhante
            else: 
                color_map.append('gray')

        # 4. Desenha os Nós e Arestas
        nx.draw(self.G, pos, 
                with_labels=True, 
                node_color=color_map, 
                node_size=3500,           # Nós grandes
                font_size=9,              # Fonte legível
                font_color='white',       # Texto Branco
                font_weight='bold',
                edge_color='#666666',     # Linhas cinza discreto
                width=2)                  # Linhas mais grossas

        # 5. O Pulo do Gato: Escrever o nome da relação NA LINHA
        edge_labels = nx.get_edge_attributes(self.G, 'relation')
        nx.draw_networkx_edge_labels(self.G, pos, 
                                   edge_labels=edge_labels, 
                                   font_color='#ffff00',  # Amarelo Neon para chamar atenção
                                   font_size=8,
                                   bbox=dict(facecolor='black', edgecolor='none', alpha=0.7)) # Fundo preto no texto

        plt.title("ANHANGÁ INTELLIGENCE MAP [TOP SECRET]", color='#00ff00', fontsize=16, weight='bold')
        
        # Remove as bordas do gráfico para ficar limpo
        plt.gca().margins(0.1, 0.1)
        plt.axis("off")
        
        print("[*] Abrindo visualização tática...")
        plt.show()