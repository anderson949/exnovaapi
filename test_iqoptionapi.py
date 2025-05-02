from exnovaapi.stable_api import Exnova
import time
import logging
import datetime
import sys

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔐 Credenciais de acesso
email = "cassioms764@gmail.com"
senha = "SJN@/8520"

print("=== PROGRAMA DE TESTE BULLEX API ===")
print("Iniciando conexão com a plataforma...")

# 🔌 Conectando à Bullex
Iq = Exnova(email, senha)

# Tentativas de conexão
max_attempts = 3
attempts = 0

while attempts < max_attempts:
    try:
        print(f"Tentativa de conexão {attempts+1}/{max_attempts}...")
        status, message = Iq.connect()
        
        if status:
            print("✅ Conectado com sucesso!")
            break
        else:
            print(f"❌ Falha na conexão: {message}")
    except Exception as e:
        print(f"❌ Erro durante a conexão: {str(e)}")
    
    attempts += 1
    if attempts < max_attempts:
        print("Tentando novamente em 5 segundos...")
        time.sleep(5)
    else:
        print("Número máximo de tentativas atingido. Verifique a URL do servidor e suas credenciais.")
        sys.exit(1)

# 🧾 Selecionando conta DEMO
print("\n=== INFORMAÇÕES DA CONTA ===")
Iq.change_balance("PRACTICE")

# 🔎 Verificando tipo de conta ativa
print("💼 Tipo de conta:", Iq.get_balance_mode())
print("💰 Saldo disponível:", Iq.get_balance())
print("💱 Moeda da conta:", Iq.get_currency())

# 📊 Obtendo lista de ativos disponíveis
print("\n=== ATIVOS DISPONÍVEIS ===")
try:
    # Atualiza os códigos dos ativos disponíveis
    Iq.update_ACTIVES_OPCODE()
    
    # Obtém todos os ativos disponíveis
    all_assets = Iq.get_all_ACTIVES_OPCODE()
    
    # Lista uma amostra dos ativos disponíveis (primeiros 10)
    print(f"Total de ativos disponíveis: {len(all_assets)}")
    print("Primeiros 10 ativos:")
    for i, (asset_name, asset_id) in enumerate(list(all_assets.items())[:10]):
        print(f"{i+1}. {asset_name} (ID: {asset_id})")
    
    # Selecionar um ativo para usar nas operações
    selected_asset = "EURUSD-op"
    print(f"\nAtivo selecionado para operações: {selected_asset}")
    
except Exception as e:
    print(f"❌ Erro ao obter ativos: {str(e)}")

# 📈 Coletando histórico de candles do ativo selecionado
print("\n=== HISTÓRICO DE CANDLES ===")
try:
    # Obtém timestamp atual
    now = int(time.time())
    
    # Obtém candles do último dia (86400 segundos = 1 dia)
    # Parâmetros: ativo, intervalo em segundos, quantidade de candles, timestamp final
    candles = Iq.get_candles(selected_asset, 60, 24, now)
    
    print(f"Obtidos {len(candles)} candles do ativo {selected_asset}")
    print("Últimos 5 candles:")
    for i, candle in enumerate(candles[-5:]):
        candle_time = datetime.datetime.fromtimestamp(candle['from']).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{candle_time} - Abertura: {candle['open']}, Fechamento: {candle['close']}, Máx: {candle['max']}, Mín: {candle['min']}")
    
except Exception as e:
    print(f"❌ Erro ao obter histórico: {str(e)}")

# 💰 Executando ordem binária
print("\n=== OPERAÇÃO BINÁRIA ===")
try:
    # Parâmetros: valor, ativo, direção (call/put), expiração em minutos
    amount = 1  # Valor da operação
    direction = "call"  # Direção (call = compra, put = venda)
    expiration = 1  # Expiração em minutos
    
    print(f"Executando ordem binária: {direction.upper()} em {selected_asset}, valor: {amount}, expiração: {expiration} min")
    status, order_id = Iq.buy(amount, selected_asset, direction, expiration)
    
    if status:
        print(f"✅ Ordem executada com sucesso! ID: {order_id}")
        
        # Aguarda o resultado da operação
        print("Aguardando resultado...")
        time.sleep(expiration * 60 + 5)  # Tempo de expiração + 5 segundos
        
        # Verifica resultado
        result = Iq.check_win_v4(order_id)
        print(f"Resultado: {result[0]}, Lucro/Prejuízo: {result[1]}")
    else:
        print(f"❌ Falha ao executar ordem: {order_id}")
    
except Exception as e:
    print(f"❌ Erro na operação binária: {str(e)}")

# 💹 Executando ordem digital
print("\n=== OPERAÇÃO DIGITAL ===")
try:
    # Parâmetros: ativo, valor, direção (call/put), duração em minutos
    amount = 1  # Valor da operação
    direction = "call"  # Direção (call = compra, put = venda)
    duration = 1  # Duração em minutos
    
    print(f"Executando ordem digital: {direction.upper()} em {selected_asset}, valor: {amount}, duração: {duration} min")
    status, order_id = Iq.buy_digital_spot(selected_asset, amount, direction, duration)
    
    if status:
        print(f"✅ Ordem digital executada com sucesso! ID: {order_id}")
        
        # Aguarda o resultado da operação
        print("Aguardando resultado...")
        time.sleep(duration * 60 + 5)  # Tempo de expiração + 5 segundos
        
        # Verifica resultado
        result = Iq.check_win_digital_v2(order_id)
        
        # Corrige a interpretação do resultado - se o valor é negativo, foi perda
        is_win = result[0] and result[1] > 0
        result_text = "Ganhou" if is_win else "Perdeu"
        
        print(f"Resultado: {result_text}, Lucro/Prejuízo: {result[1]}")
    else:
        print(f"❌ Falha ao executar ordem digital: {order_id}")
    
except Exception as e:
    print(f"❌ Erro na operação digital: {str(e)}")

# Função para implementar martingale
def apply_martingale(base_amount, loss_count, martingale_factor=2):
    """Calcula o próximo valor para martingale após uma perda"""
    return base_amount * (martingale_factor ** loss_count)

# Função para verificar resultado sem bloquear (polling)
def check_operation_result(Iq, order_id, is_digital=False, check_interval=1, timeout=120):
    """Verifica o resultado de uma operação sem bloquear por muito tempo"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            if is_digital:
                # Para operações digitais
                result = Iq.check_win_digital_v2(order_id)
                if result[0] is not None:  # Quando None, ainda está em andamento
                    is_win = result[0] and result[1] > 0
                    return True, is_win, result[1]  # Completo, resultado, lucro/prejuízo
            else:
                # Para operações binárias
                result = Iq.check_win_v4(order_id)
                if result[0] in ['win', 'equal', 'loose']:  # Se tiver resultado
                    is_win = result[0] == 'win'
                    return True, is_win, result[1]  # Completo, resultado, lucro/prejuízo
        except Exception as e:
            print(f"Erro ao verificar resultado: {e}")
        
        # Aguarda um curto período antes de verificar novamente
        time.sleep(check_interval)
    
    # Timeout - não conseguiu obter resultado
    return False, False, 0

# 💰 Executando operações com martingale
print("\n=== OPERAÇÃO COM MARTINGALE ===")
try:
    # Configuração inicial
    base_amount = 1  # Valor inicial da operação
    max_martingale = 3  # Número máximo de martingales
    martingale_factor = 2  # Fator de multiplicação (2x, 3x, etc.)
    direction = "call"  # Direção inicial (call/put)
    expiration = 1  # Expiração em minutos
    
    # Estatísticas da sessão
    session_profit = 0
    win_count = 0
    loss_count = 0
    
    # Loop de operações com martingale
    current_amount = base_amount
    martingale_level = 0
    
    for attempt in range(max_martingale + 1):  # +1 porque a primeira operação não é martingale
        # Executa operação
        print(f"\nOperação #{attempt+1}: {direction.upper()} {current_amount} em {selected_asset}")
        status, order_id = Iq.buy(current_amount, selected_asset, direction, expiration)
        
        if not status:
            print(f"❌ Falha ao executar ordem: {order_id}")
            break
            
        print(f"✅ Ordem #{attempt+1} executada com sucesso! ID: {order_id}")
        print(f"Verificando resultado (pode levar até {expiration} minutos)...")
        
        # Verifica resultado sem bloquear por muito tempo
        completed, is_win, profit = check_operation_result(Iq, order_id)
        
        if not completed:
            print("⚠️ Tempo excedido ao verificar resultado. Tentando próxima operação...")
            continue
            
        # Processa resultado
        if is_win:
            print(f"✅ GANHOU! Lucro: {profit}")
            session_profit += profit
            win_count += 1
            # Reseta para valor inicial após ganhar
            current_amount = base_amount
            martingale_level = 0
            # Opcionalmente, pode trocar a direção aqui
            # direction = "put" if direction == "call" else "call"
            break  # Sai do loop de martingale após ganhar
        else:
            print(f"❌ PERDEU! Prejuízo: {profit}")
            session_profit += profit
            loss_count += 1
            martingale_level += 1
            
            if martingale_level <= max_martingale:
                # Aplica martingale para próxima operação
                current_amount = apply_martingale(base_amount, martingale_level, martingale_factor)
                print(f"Aplicando martingale nível {martingale_level}. Próximo valor: {current_amount}")
                # Opcionalmente, pode manter ou inverter a direção
                # direction = "put" if direction == "call" else "call"
            else:
                print("Atingido número máximo de martingales sem sucesso.")
                break
    
    # Resumo da sessão
    print("\n=== RESUMO DA SESSÃO ===")
    print(f"Vitórias: {win_count}")
    print(f"Derrotas: {loss_count}")
    print(f"Lucro/Prejuízo final: {session_profit}")
    
except Exception as e:
    print(f"❌ Erro nas operações: {str(e)}")

print("\n=== TESTE CONCLUÍDO ===")
