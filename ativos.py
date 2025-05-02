from exnovaapi.stable_api import Exnova
import json


email = "cassioms764@gmail.com"
senha = "SJN@/8520"
api = Exnova(email, senha)

status, message = api.connect()
        
if status:
    print("✅ Conectado com sucesso!")

# Atualizar e pegar os ativos
api.update_ACTIVES_OPCODE()
ativos = api.get_all_ACTIVES_OPCODE()
print("Ativos disponíveis:", ativos)

# Salvar em um arquivo JSON
with open('ativos.json', 'w', encoding='utf-8') as f:
    json.dump(ativos, f, ensure_ascii=False, indent=4)

