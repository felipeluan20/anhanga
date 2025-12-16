# test_v2.py
from core.engine import InvestigationEngine

engine = InvestigationEngine()
# Pipeline: Pasta.Arquivo
pipeline = ['fincrime.pix_decoder'] 

print(">>> Testando Anhangá v2.0...")
# Pix de teste do Banco Central
pix_teste = "00020126580014br.gov.bcb.pix0136123e4567-e12b-12d1-a456-426655440000520400005303986540510.005802BR5913Fulano de Tal6008BRASILIA62070503***63041D3D"

res = engine.run_pipeline(pix_teste, pipeline)

print("\n>>> Resultados:")
for r in res:
    print(r)