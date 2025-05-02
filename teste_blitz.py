from exnovaapi.stable_api import Exnova
import time
import logging
import datetime
import sys

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Credenciais de acesso (substitua por suas credenciais)
email = "cassioms764@gmail.com"
senha = "SJN@/8520"

print("=== PROGRAMA DE TESTE BLITZ OPTION ===")
print("Iniciando conexão com a plataforma exnova...")

# Conectando à plataforma
exnova = Exnova(email, senha)


# Tentativas de conexão
max_attempts = 3
attempts = 0

while attempts < max_attempts:
    try:
        print(f"Tentativa de conexão {attempts+1}/{max_attempts}...")
        status, message = exnova.connect()

        # Atualizar e pegar os ativos
        #exnova.update_ACTIVES_OPCODE()
        #ativos = exnova.get_all_ACTIVES_OPCODE()
        #print("Ativos disponíveis:", ativos)
        
        if status:
            print("✅ Conectado com sucesso!")
            break
        else:
            print(f"❌ Falha na conexão: {message}")
            if message == "2FA":
                sms_code = input("Digite o código SMS recebido: ")
                status, message = exnova.connect_2fa(sms_code)
                if status:
                    print("✅ Conectado com sucesso!")
                    break
                else:
                    print(f"❌ Falha na autenticação 2FA: {message}")
    except Exception as e:
        print(f"❌ Erro durante conexão: {str(e)}")
    
    attempts += 1
    if attempts < max_attempts:
        print("Tentando novamente em 5 segundos...")
        time.sleep(5)

if attempts >= max_attempts:
    print("Não foi possível conectar após várias tentativas. Saindo do programa.")
    sys.exit(1)

# Verificando o saldo e usando a conta de PRÁTICA
print("\n=== INFORMAÇÕES DA CONTA ===")
exnova.change_balance("PRACTICE")
balance = exnova.get_balance()
print(f"Saldo atual: {balance}")

# Parâmetros para a compra de uma opção Blitz
ativo = "GBPCAD-OTC"  # Escolha um ativo disponível
valor = 1  # Investimento (ajuste conforme necessário)
direcao = "call"  # 'call' para ALTA ou 'put' para BAIXA
expiracao = 5  # tempo em segundos (3, 5, 10 segundos)

# Verificar se o mercado está aberto para este ativo
print(f"\nPreparando para comprar opção Blitz: {ativo} - {direcao.upper()} - {expiracao}s")
time.sleep(1)  # Pequena pausa para sincronização

# Efetuando a compra
print("Realizando compra...")
try:
    resultado, id_ordem = exnova.buy_blitz(ativo, valor, direcao, expiracao)
    #resultado, id_ordem  = exnova.buy_digital_spot_v2(ativo, valor, direcao, 1)
    
    if resultado:
        print(f"✅ Compra realizada com sucesso! ID da ordem: {id_ordem}")
        
        # Aguardando o resultado da operação
        print(f"Aguardando {expiracao} segundos para expiração...")
        time.sleep(expiracao + 2)  # +2 para garantir que a ordem seja processada
        
        try:
            # Verificando o resultado
            print("Verificando resultado da operação...")
            resultado_win, lucro = exnova.check_win_v4(id_ordem)
            
            if resultado_win == "win":
                print(f"✅ GANHOU! Lucro: {lucro}")
            elif resultado_win == "equal":
                print("⚠️ EMPATE! Valor devolvido")
            else:
                print(f"❌ PERDEU! Perda: {lucro}")
        except Exception as e:
            print(f"❌ Erro ao verificar resultado: {str(e)}")
    else:
        print(f"❌ Falha na compra: {id_ordem}")
        
        # Tentar fornecer mais informações sobre o erro
        print("\nDetalhes do erro:")
        print("1. Verifique se a opção Blitz está disponível para este ativo")
        print("2. Verifique se o mercado está aberto no momento")
        print("3. Verifique se o valor está dentro dos limites permitidos")
except Exception as e:
    print(f"❌ Erro durante a compra: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n=== TESTE FINALIZADO ===")
