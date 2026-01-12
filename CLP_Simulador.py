from pyModbusTCP.server import ModbusServer, DataBank
import time
import random
from datetime import datetime

HOST = "127.0.0.3"
PORT = 502

# ===== MAPA DE REGISTRADORES =====
# Ajuste se seu SCADA usar endereços específicos

REG_MAP = {
    "VelocidadeEsteira": 0,
    "torque": 1,
    "FrequenciaRotacao": 2,
    "CargaEsteira": 3,
    "TempCarc": 4,
    "CorrenteMedia": 5,
    "PotAtivaTotal": 6,
    "PotReativaTotal": 7,
    "PotAparenteTotal": 8,
    "FrequenciaRede": 9,
    "dppRS": 10,
    "dppST": 11,
    "dppTR": 12,
    "CorrenteR": 13,
    "CorrenteS": 14,
    "CorrenteT": 15,
    "tempR": 16,
    "tempS": 17,
    "tempT": 18,
    "THDCorrenteR": 19,
    "THDCorrenteS": 20,
    "THDCorrenteT": 21,
    "StatusPID": 22,
    "TipoPartida": 23,
    "SetPoint": 24,
    "VarManip": 25,
    "ControleP": 26,
    "ControleI": 27,
    "ControleD": 28,
}

def randomize():
    return {
        "VelocidadeEsteira": random.randint(0, 100),
        "torque": random.randint(0, 200),
        "FrequenciaRotacao": random.randint(0, 1800),
        "CargaEsteira": random.randint(0, 100),
        "TempCarc": random.randint(20, 90),
        "CorrenteMedia": random.randint(0, 100),
        "PotAtivaTotal": random.randint(0, 5000),
        "PotReativaTotal": random.randint(0, 5000),
        "PotAparenteTotal": random.randint(0, 5000),
        "FrequenciaRede": 60,
        "dppRS": random.randint(210, 240),
        "dppST": random.randint(210, 240),
        "dppTR": random.randint(210, 240),
        "CorrenteR": random.randint(0, 50),
        "CorrenteS": random.randint(0, 50),
        "CorrenteT": random.randint(0, 50),
        "tempR": random.randint(20, 90),
        "tempS": random.randint(20, 90),
        "tempT": random.randint(20, 90),
        "THDCorrenteR": random.randint(0, 20),
        "THDCorrenteS": random.randint(0, 20),
        "THDCorrenteT": random.randint(0, 20),
        "StatusPID": random.randint(0, 1),
        "TipoPartida": random.randint(1, 3),
    }

def main():
    server = ModbusServer(host=HOST, port=PORT, no_block=True)
    server.start()

    print("====================================")
    print(" CLP MODBUS TCP SIMULADOR ATIVO ")
    print(f" IP: {HOST}")
    print(f" Porta: {PORT}")
    print("====================================")

    try:
        while True:
            values = randomize()

            for name, addr in REG_MAP.items():
                if name in values:
                    DataBank.set_words(addr, [values[name]])

            # Log
            print(datetime.now().strftime("%H:%M:%S"), values)

            time.sleep(1)

    except KeyboardInterrupt:
        print("Encerrando CLP...")
        server.stop()

if __name__ == "__main__":
    main()
