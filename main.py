# Arquivo: anhanga/main.py
import typer
import sys
import os
from rich.console import Console
from rich.panel import Panel

# Setup de Path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Imports
from modules.fincrime.pix_decoder import PixForensics
from modules.infra.hunter import InfraHunter, ShodanIntel, CertificateHunter
from modules.infra.analyzer import ContractAnalyzer
from modules.fincrime.validator import LaranjaHunter
from modules.graph.builder import GraphBrain
from core.database import CaseManager
from core.config import ConfigManager # <--- NOVO GERENCIADOR

app = typer.Typer(help="Anhangá - Cyber Defense Framework")
console = Console()
db = CaseManager()
cfg = ConfigManager()

@app.command()
def intro():
    """Exibe o banner e status do sistema."""
    banner = """
    [bold green]
                                                                          █
                                                                         █   
       ▄▄▄       ███▄    █  ██░ ██  ▄▄▄       ███▄    █   ▄████  ▄▄▄    █  
      ▒████▄     ██ ▀█   █ ▓██░ ██▒▒████▄     ██ ▀█   █  ██▒ ▀█▒▒████▄    
      ▒██  ▀█▄  ▓██  ▀█ ██▒▒██▀▀██░▒██  ▀█▄  ▓██  ▀█ ██▒▒██░▄▄▄░▒██  ▀█▄  
      ░██▄▄▄▄██ ▓██▒  ▐▌██▒░▓█ ░██ ░██▄▄▄▄██ ▓██▒  ▐▌██▒░▓█  ██▓░██▄▄▄▄██ 
       ▓█   ▓██▒▒██░   ▓██░░▓█▒░██▓ ▓█   ▓██▒▒██░   ▓██░░▒▓███▀▒ ▓█   ▓██▒
       ▒▒   ▓▒█░░ ▒░   ▒ ▒  ▒ ░░▒░▒ ▒▒   ▓▒█░░ ▒░   ▒ ▒  ░▒   ▒  ▒▒   ▓▒█░
    [/bold green]
    [bold yellow]   SWAT INTELLIGENCE FRAMEWORK v1.0[/bold yellow]
    """
    console.print(banner)
    console.print(Panel.fit("Módulos ativos: FinCrime, Infra, GraphCore.", title="Status do Sistema", border_style="green"))

@app.command()
def config(
    shodan: str = typer.Option(None, "--set-shodan", help="Salva sua API Key do Shodan permanentemente")
):
    """Configurações Globais (Salvas para sempre)."""
    if shodan:
        cfg.set_key("shodan", shodan)
        console.print("[green][V] Chave Shodan salva com sucesso![/green]")

@app.command()
def start():
    """Inicia nova operação (ZERA O CASO ATUAL)."""
    db.nuke()
    console.print("[bold green][*] Operação Limpa Iniciada.[/bold green]")

@app.command()
def add_pix(
    pix: str = typer.Option(..., "--pix", "-p"),
    link_url: str = typer.Option(None, "--link", "-l", help="URL associada a este pagamento (Cria Vínculo)")
):
    """Adiciona Pix e opcionalmente vincula a um site."""
    decoder = PixForensics(pix)
    data = decoder.analyze()
    
    # Adiciona Entidade
    nome = data['merchant_name']
    doc = data['pix_key']
    db.add_entity(nome, doc, role="Recebedor Pix")
    
    console.print(f"[green][+] Alvo Financeiro:[/green] {nome}")
    
    # CRIA O VÍNCULO REAL (Se o usuário informou a URL)
    if link_url:
        # Garante que a infra existe antes de vincular
        db.add_infra(link_url, ip="Desconhecido") 
        db.add_relation(nome, link_url, "recebeu_pagamento_de")
        console.print(f"[bold cyan][LINK] Vínculo forense criado: {nome} <--> {link_url}[/bold cyan]")

@app.command()
def add_url(url: str = typer.Option(..., "--url", "-u")):
    """Analisa Infra. Usa a chave Shodan salva na config."""
    console.print(f"[blue][*] Investigando: {url}[/blue]")
    
    # 1. Recupera Chave da Config Global
    shodan_key = cfg.get_key("shodan")
    if not shodan_key:
        console.print("[yellow][!] AVISO: Chave Shodan não configurada. Use 'python main.py config --set-shodan KEY'[/yellow]")
    
    # 2. Executa Hunter (Igual v2.1)
    hunter = InfraHunter(url)
    target_ip = hunter.resolve_ip()
    hash_val, _ = hunter.get_favicon_hash()
    
    report = f"IP: {target_ip}\nHash: {hash_val}"
    
    # 3. Shodan (Se tiver chave)
    if shodan_key:
        shodan_tool = ShodanIntel(shodan_key)
        intel = shodan_tool.enrich_target(target_ip, hash_val)
        if not intel.get("error"):
            report += f"\n\n[SHODAN]: {intel['strategy']}\nDados coletados."
            
            # IA Analysis (Opcional)
            try:
                analyst = ContractAnalyzer(url)
                ai_res = analyst.analyze_shodan_data(str(intel['data']))
                report += f"\n\n[IA]:\n{ai_res}"
            except: pass
            
    db.add_infra(url, ip=str(target_ip), extra_info=report)
    console.print(Panel(report, title="Relatório Infra", border_style="cyan"))

@app.command()
def graph():
    """Gera o Grafo APENAS com vínculos confirmados."""
    brain = GraphBrain()
    case = db.get_full_case()
    
    # 1. Adiciona Nós (Entidades e Infra)
    for ent in case['entities']:
        brain.add_fincrime_data(ent['name'], ent['document'])
    for inf in case['infra']:
        brain.add_infra_data(inf['domain'], inf['ip'])
        
    # 2. Adiciona APENAS Relações Reais (A Correção Lógica)
    # O loop "for x in entities / for y in infra" FOI REMOVIDO.
    count = 0
    for rel in case['relations']:
        brain.connect_entities(rel['source'], rel['target'], relation_type=rel['type'])
        count += 1
        
    if count == 0:
        console.print("[yellow][!] Nenhuma conexão explícita encontrada. O grafo mostrará apenas nós soltos.[/yellow]")
        console.print("Dica: Use '--link site.com' ao adicionar um Pix.")
        
    brain.plot_investigation()

if __name__ == "__main__":
    app()