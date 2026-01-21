🏭 **Supervisório de Esteira Transportadora (SCADA)**

Sistema supervisório desenvolvido em Python + Kivy para monitoramento e controle de uma esteira transportadora industrial, utilizando Modbus TCP, gráficos em tempo real, histórico de dados e persistência em banco de dados via ORM (SQLAlchemy).

📌 **Funcionalidades**

  📊 Monitoramento em tempo real de grandezas mecânicas, elétricas e térmicas
  
  🔌 Comunicação Modbus TCP com CLP

  📈 Gráficos dinâmicos com escalas automáticas por grandeza

  🗂️ Histórico de dados com seleção por intervalo de tempo

  🧠 Persistência em banco de dados SQLite via ORM

  ⚙️ Controle de motor (Direta, Soft-Start e Inversor)

  🎛️ Controle PID com modos Automático e Manual

  🧩 Arquitetura modular e extensível

  🧱 **Arquitetura do Projeto**

O projeto segue uma arquitetura modular, separando responsabilidades de forma clara:
    
    ├── main_orm.py                 # Ponto de entrada da aplicação
    ├── mainwidget_dbrefactor.py    # Widget principal (lógica SCADA)
    │
    ├── popups.py                   # Popups de medições, PID, comandos e gráficos
    ├── popups.kv                   # Layouts KV dos popups
    ├── mainwidget.kv               # Layout principal da interface
    │
    ├── timeseriesgraph.py          # Gráficos temporais + GRAPH_CONFIG
    │
    ├── db_scada.py                 # Engine, Base e Session (SQLAlchemy)
    ├── models_scada.py             # Modelo ORM dinâmico
    ├── persistencia_scada.py       # Camada de persistência
    │
    └── README.md

🔌 **Comunicação Modbus**

O sistema utiliza Modbus TCP e diferencia explicitamente o tipo de cada registrador:

FP → Float 32-bit (2 holding registers)

4x → Inteiro (1 holding register)

Exemplo de mapeamento:

    'VelocidadeEsteira': {"addr": 724, "tipo": "FP"},
    'CorrenteR':         {"addr": 840, "tipo": "4x"},

Essa abordagem evita leituras incorretas e garante compatibilidade com o CLP.

📊 Gráficos e Escalas

Todas as grandezas possuem configuração centralizada em GRAPH_CONFIG:

    GRAPH_CONFIG = {
      "VelocidadeEsteira": {
        "label": "Velocidade da Esteira",
        "unit": "m/min",
        "ymin": 0,
        "ymax": 10
      }
    }

Benefícios:

- Escalas corretas por grandeza
- Unidades padronizadas
- Facilidade para adicionar novas variáveis

🗄️ **Persistência de Dados**

- Banco de dados: SQLite
- ORM: SQLAlchemy
- Modelo gerado dinamicamente a partir das tags Modbus
- Seguro para uso com threads (Kivy)
- O banco é criado automaticamente no primeiro uso.

⚙️ **Controle PID**

- Modos:

  - Automático
  - Manual

- Escrita segura no CLP:

  - VarManip só é enviada em modo manual

- Limites físicos respeitados (0–100%)
- Evita escrita contínua indevida de parâmetros

📦 **Dependências**

Instalação via pip

    pip install kivy
    pip install kivy-garden
    pip install kivy-garden.graph
    pip install pyModbusTCP
    pip install pymodbus
    pip install sqlalchemy

⚠️ Recomendado utilizar ambiente virtual (venv).

▶️ **Como Executar**

    python main_orm.py
    
Antes de executar:

- Verifique o IP, porta do CLP e caminho do *db_path*
- Confirme o mapeamento dos sensores e atuadores do Modbus em *main_orm.py*











