from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup, DataGraphPopup, PidPopup, MedicoesPopup, ComandoPopup, TemperaturaPopup, HistGraphPopup, SelectDataGraphPopup
from pyModbusTCP.client import ModbusClient
from kivy.core.window import Window
from threading import Thread
from time import sleep
from datetime import datetime
import random
import struct
from kivy_garden.graph import LinePlot
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

from persistencia_scada import ScadaPersistencia
from timeseriesgraph import GRAPH_CONFIG


class MainWidget(BoxLayout):
    "Criação da classe principal/widget principal da aplicação"

    _updateThread = None
    _updateWidgets = True
    _tags = {}
    _max_points = 20

    def __init__(self, **kwargs):
        super().__init__()
        self._scan_time = kwargs.get('scan_time')
        self._server_ip = kwargs.get("server_ip")
        self._server_port = kwargs.get("server_port")

        self._modbusClient = ModbusClient(host=self._server_ip, port=self._server_port)
        self._modbusPopup = ModbusPopup(server_ip=self._server_ip, server_port=self._server_port)
        self._scanPopup = ScanPopup(self._scan_time)

        self._meas = {'timestamp': None, 'values': {}}
        self._tags = kwargs.get('modbus_addrs')

        for key, value in self._tags.items():
            if key == 'VelocidadeEsteira':
                plot_color = (1, 0, 0, 1)
            else:
                plot_color = (random.random(), random.random(), random.random(), 1)
            self._tags[key]["color"] = plot_color

        self._graph = DataGraphPopup(self._max_points, self._tags['VelocidadeEsteira']['color'])
        self._hgraph = HistGraphPopup(tags=self._tags)

        self._db = ScadaPersistencia(kwargs.get('db_path'), self._tags)

        self._pidPopup = PidPopup()

        self._medicoesPopup = MedicoesPopup()
        self._comandoPopup = ComandoPopup()
        self._TemperaturaPopup = TemperaturaPopup()
        self._selectData = SelectDataGraphPopup()
        self._selected_grandeza = 'VelocidadeEsteira'
        # Tags que são comandos
        self._writable_keys = ['PartidInv', 'PartidaST', 'PartidaDir', 'VelInv', 'TipoPID', 'TipoPartida', 'ControleP', 'ControleI', 'ControleD', 'SetPoint', 'VarManip', 'RampaAcelST', 'RampaDesacelST', 'RampaAcelInv', 'RampaDesacelInv']
        # Evita escrever parâmetros PID continuamente
        self._enable_pid_write = False

    def startDataRead(self, ip, port):
        self._server_ip = ip
        self._server_port = port
        self._modbusClient.host = self._server_ip
        self._modbusClient.port = self._server_port
        try:
            Window.set_system_cursor("wait")
            self._modbusClient.open()
            Window.set_system_cursor("arrow")
            if self._modbusClient.is_open:
                self._updateThread = Thread(target=self.updater, daemon=True)
                self._updateThread.start()
                self.ids.img_con.source = "imgs/conectado.png"
                self._modbusPopup.dismiss()
            else:
                self._modbusPopup.setInfo("Falha na conexão com o servidor")
        except Exception as e:
            print("Erro:", e.args)

    def updater(self):
        try:
            while self._updateWidgets:
                self.readData()

                # Atualiza Popups de medições
                try:
                    self._medicoesPopup.update(self._meas)
                    self._TemperaturaPopup.update(self._meas)
                except Exception as e:
                    print ("Erro Medicoes/Temperaturas:",e)

                # Atualiza os comandos escolhidos no popup
                self._comandoPopup.update(self._meas)

                # Atualiza parâmetros do PID
                self._pidPopup.update(self._meas)

                # Envia os comandos para o CLP
                self.writeData(self._meas)

                self.updateGUI()
                self._db.insertData(self._meas)

                sleep(self._scan_time / 1000)
        except Exception as e:
            self._modbusClient.close()
            print("Erro:", e)


    def readData(self):
        self._meas['timestamp'] = datetime.now()
        for key, value in self._tags.items():
            if value["tipo"]=="FP":
                self._meas['values'][key] = self.lerFloat(value['addr'])
            elif value["tipo"]=="4x":
                self._meas['values'][key] = self._modbusClient.read_holding_registers(value['addr'])[0]

    def updateSelectedGrandeza(self, grandeza):
        self._selected_grandeza = grandeza

        # ajusta escala do popup de gráfico
        try:
            self._graph.set_grandeza(grandeza)
        except Exception as e:
            print("Erro ao trocar grandeza no gráfico:", e)

        # força atualização da GUI e do gráfico
        self.updateGUI()

    def updateSelectedGrandezaHist(self, grandeza):
        """
        Chamado pelo Spinner do HistGraphPopup quando o usuário escolhe uma grandeza.
        """
        self._selected_hist_grandeza = grandeza

        # ajusta escala / label do gráfico de histórico
        try:
            self._hgraph.set_grandeza(grandeza)
        except Exception as e:
            print("Erro ao trocar grandeza no histórico:", e)

        # busca os dados para o intervalo de tempo atual
        self.getDataDB()


    def updateGUI(self):
        self.ids['VelocidadeEsteira'].text = (str(round(self._meas['values']['VelocidadeEsteira'], 2)) + ' m/min')
        self.ids['FrequenciaRotacao'].text = (str(round(self._meas['values']['FrequenciaRotacao'], 2)) + ' RPM')
        self.ids['torque'].text = (str(round(self._meas['values']['torque'], 2)) + ' N.m')
        self.ids['CargaEsteira'].text = (str(round(self._meas['values']['CargaEsteira'], 2)) + ' Kgf/cm²')
        self.ids['TempCarc'].text = (str(round(self._meas['values']['TempCarc'], 1)) + ' °C')
        try:
            valor = self._meas['values'][self._selected_grandeza]
        except KeyError:
            return

        self._graph.ids.graph.updateGraph((self._meas['timestamp'], valor), 0)

    def get_regua_ratio(self, tag: str) -> float:
        """
        Retorna um valor entre 0 e 1 indicando o quanto a régua deve ser preenchida
        para a 'tag' informada, com base em GRAPH_CONFIG e no valor atual de _meas.
        """
        try:
            cfg = GRAPH_CONFIG.get(tag)
            if cfg is None:
                # tenta variação de maiúscula/minúscula
                alt = tag[0].upper() + tag[1:]
                cfg = GRAPH_CONFIG.get(alt)
                if cfg is None:
                    return 0.0

            val = self._meas['values'].get(tag)
            if val is None:
                return 0.0

            ymin = cfg.get("ymin", 0.0)
            ymax = cfg.get("ymax", 0.0)
            if ymax <= ymin:
                return 0.0

            r = (val - ymin) / float(ymax - ymin)
            if r < 0:
                r = 0.0
            if r > 1:
                r = 1.0
            return r
        except Exception:
            return 0.0


    def stopRefresh(self):
        self._updateWidgets = False
        try:
            self._db.close()
        except Exception:
            pass

    def getDataDB(self):
        try:
            init_t = self.parseDTString(self._hgraph.ids.txt_init_time.text)
            final_t = self.parseDTString(self._hgraph.ids.txt_final_time.text)

            # grandeza escolhida no Spinner do popup de histórico
            coluna = self._hgraph.ids.spn_grandeza.text

            if init_t is None or final_t is None or not coluna:
                return

            cols = [coluna, 'timestamp']
            dados = self._db.selectData(cols, init_t, final_t)
            if dados is None or len(dados['timestamp']) == 0:
                return

            # limpa todos os plots anteriores do gráfico de histórico
            self._hgraph.ids.graph.clearPlots()

            # cria um único plot para a grandeza selecionada
            valores = dados[coluna]
            p = LinePlot(line_width=1.5, color=self._tags[coluna]['color'])
            p.points = [(x, valores[x]) for x in range(len(valores))]
            self._hgraph.ids.graph.add_plot(p)

            # ajusta eixo X para o número de pontos e atualiza labels de tempo
            self._hgraph.ids.graph.xmin = 0
            self._hgraph.ids.graph.xmax = len(valores)
            self._hgraph.ids.graph.update_x_labels(dados['timestamp'])

        except Exception as e:
            print("Erro getDataDB: ", e.args)


    def parseDTString(self, datetime_str):
        try:
            return datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
        except Exception as e:
            print("Erro: ", e.args)
            return None

    
    def _float_to_regs(self, value: float):
        """Converte float 32-bit para 2 holding registers (wordorder LITTLE), compatível com lerFloat()."""
        b = struct.pack('>f', float(value))  # bytes big-endian
        w0 = int.from_bytes(b[0:2], 'big')
        w1 = int.from_bytes(b[2:4], 'big')
        return [w1, w0]  # wordorder little (swap)

    def escreverInt(self, addr: int, value: int) -> bool:
        if not self._modbusClient.is_open:
            self._modbusClient.open()

        ok = self._modbusClient.write_single_register(addr, int(value))
        print(f"[WRITE INT] addr={addr} value={value} ok={ok}")
        return bool(ok)

    def escreverFloat(self, addr: int, value: float) -> bool:
        regs = self._float_to_regs(value)
        if not self._modbusClient.is_open:
            self._modbusClient.open()

        ok = self._modbusClient.write_multiple_registers(addr, regs)
        print(f"[WRITE FLOAT] addr={addr} value={value} regs={regs} ok={ok}")
        return bool(ok)


    def writeData(self, meas):
        # Motor/comandos: 1 holding register (INT)
        MOTOR_INT_TAGS = [
            "TipoPartida",      
            "VelInv",
            "RampaAcelInv",
            "RampaDesacelInv",
            "RampaAcelST",
            "RampaDesacelST",
            "PartidInv",
            "PartidaST",
            "PartidaDir",
        ]

        # PID: provavelmente 32-bit float (2 holding registers)
        PID_FLOAT_TAGS = [
            "ControleP",
            "ControleI",
            "ControleD",
            "SetPoint",
            "VarManip",
        ]

        #Se PID for int
        PID_INT_TAGS = ["TipoPID"]

        # 1) Escreve INTs do motor (1 register)
        for k in MOTOR_INT_TAGS:
            v = self._meas["values"].get(k)
            if v is not None:
                self.escreverInt(self._tags[k]["addr"], int(v))

        # 2) Escreve TipoPID como INT (se aplicável)
        for k in PID_INT_TAGS:
            v = self._meas["values"].get(k)
            if v is not None:
                self.escreverInt(self._tags[k]["addr"], int(v))

        # 3) Escreve floats do PID (2 registers)
        for k in PID_FLOAT_TAGS:
            v = self._meas["values"].get(k)
            if v is not None:
                self.escreverFloat(self._tags[k]["addr"], float(v))



    def lerFloat(self, addr):
        result = self._modbusClient.read_holding_registers(addr, 2)
        decoder = BinaryPayloadDecoder.fromRegisters(
            result, 
            byteorder=Endian.Big, wordorder=Endian.Little)
        return decoder.decode_32bit_float()