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

"classe principal da aplicação"
class MainWidget(BoxLayout):
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

        for key, value in kwargs.get('modbus_addrs').items():
            if key == 'VelocidadeEsteira':
                plot_color = (1, 0, 0, 1)
            else:
                plot_color = (random.random(), random.random(), random.random(), 1)
            self._tags[key] = {'addr': value, 'color': plot_color}

        self._graph = DataGraphPopup(self._max_points, self._tags['VelocidadeEsteira']['color'])
        self._hgraph = HistGraphPopup(tags=self._tags)
        self._db = ScadaPersistencia(kwargs.get('db_path'), self._tags)

        self._pidPopup = PidPopup()

        self._medicoesPopup = MedicoesPopup()
        self._comandoPopup = ComandoPopup()
        self._TemperaturaPopup = TemperaturaPopup()
        self._selectData = SelectDataGraphPopup()
        self._selected_grandeza = 'VelocidadeEsteira'
        self._writable_keys = ['PartidInv', 'PartidaST', 'PartidaDir', 'VelInv', 'TipoPID', 'TipoPartida', 'ControleP', 'ControleI', 'ControleD', 'SetPoint', 'VarManip', 'RampaAcelST', 'RampaDesacelST', 'RampaAcelInv', 'RampaDesacelInv']
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
                # Atualiza os comandos escolhidos no popup
                self._comandoPopup.update(self._meas)

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
            self._meas['values'][key] = self.lerFloat(value['addr'])

    def updateSelectedGrandeza(self, grandeza):
        if grandeza in self._meas['values']:
            self._selected_grandeza = grandeza
            self._graph.ids.graph.clearGraph()
            self.updateGUI()

    def updateGUI(self):
        self.ids['VelocidadeEsteira'].text = (str(round(self._meas['values']['VelocidadeEsteira'], 2)) + ' m/min')
        self.ids['FrequenciaRotacao'].text = (str(round(self._meas['values']['FrequenciaRotacao'], 2)) + ' RPM')
        self.ids['torque'].text = (str(round(self._meas['values']['torque'], 2)) + ' N.m')
        self.ids['CargaEsteira'].text = (str(round(self._meas['values']['CargaEsteira'], 2)) + ' Kgf/cm²')

        self._graph.ids.graph.updateGraph((self._meas['timestamp'], self._meas['values'][self._selected_grandeza]), 0)

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

            cols = []
            for sensor in self._hgraph.ids.sensores.children:
                if sensor.ids.checkbox.active:
                    cols.append(sensor.id)

            if init_t is None or final_t is None or len(cols) == 0:
                return

            cols.append('timestamp')
            dados = self._db.selectData(cols, init_t, final_t)
            if dados is None or len(dados['timestamp']) == 0:
                return

            self._hgraph.ids.graph.clearPlots()
            for key, value in dados.items():
                if key == 'timestamp':
                    continue
                p = LinePlot(line_width=1.5, color=self._tags[key]['color'])
                p.points = [(x, value[x]) for x in range(0, len(value))]
                self._hgraph.ids.graph.add_plot(p)

            self._hgraph.ids.graph.xmax = len(dados[cols[0]])
            self._hgraph.ids.graph.update_x_labels(dados['timestamp'])

        except Exception as e:
            print("Erro: ", e.args)

    def parseDTString(self, datetime_str):
        try:
            return datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
        except Exception as e:
            print("Erro: ", e.args)
            return None

    "converte float para holding registerers"
    def _float_to_regs(self, value: float):
        b = struct.pack('>f', float(value))
        w0 = int.from_bytes(b[0:2], 'big')
        w1 = int.from_bytes(b[2:4], 'big')
        return [w1, w0]
    
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
        #Tags int
        INT_TAGS = [
            "PartidInv",
            "PartidaST",
            "PartidaDir",
            "TipoPartida",
            "TipoPID"
        ]

        #Tags float
        FLOAT_TAGS = [
            "VelInv",
            "RampaAcelST",
            "RampaDesacelST",
            "RampaAcelInv",
            "RampaDesacelInv",
            "ControleP",
            "ControleI",
            "ControleD",
            "SetPoint",
            "VarManip"
        ]

        #int
        for k in INT_TAGS:
            v = self._meas["values"].get(k)
            if v is not None:
                self.escreverInt(self._tags[k]["addr"], int(v))

        #float
        for k in FLOAT_TAGS:
            v = self._meas["values"].get(k)
            if v is not None:
                self.escreverFloat(self._tags[k]["addr"], float(v))
    def lerFloat(self, addr):
        result = self._modbusClient.read_holding_registers(addr, 2)
        decoder = BinaryPayloadDecoder.fromRegisters(result, byteorder=Endian.Big, wordorder=Endian.Little)
        return decoder.decode_32bit_float()