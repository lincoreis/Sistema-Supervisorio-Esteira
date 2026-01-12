from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import LinePlot

"config protocolo modbus"
class ModbusPopup (Popup):
    _info_lb = None
    
    "construtor da classe"
    def __init__(self, server_ip, server_port, **kwargs):
        super().__init__(**kwargs)
        self.ids.txt_ip.text = str(server_ip)
        self.ids.txt_port.text = str(server_port)
    
    def setInfo(self, message):
        self._info_lb = Label(text=message)
        self.ids.layout.add_widget(self._info_lb)
    
    def clearInfo(self):
        if self._info_lb is not None:
            self.ids.layout.remove_widget(self._info_lb)
    
"config tempo de varredura"
class ScanPopup(Popup):
    "construtor da classe"
    def __init__(self, scantime, **kwargs):
        super().__init__(**kwargs)
        self.ids.txt_st.text = str(scantime)

class DataGraphPopup(Popup):
    def __init__(self, xmax, plot_color, **kwargs):
        super().__init__(**kwargs)
        self.plot = LinePlot(line_width=1.5, color=plot_color)
        self.ids.graph.add_plot(self.plot)
        self.ids.graph.xmax = xmax

class LabeledCheckBoxDataGraph(BoxLayout):
    pass

"config PID"
class PidPopup(Popup):
    _SP = None
    _MV = None
    _P = None
    _I = None
    _D = None

    "construtor da classe"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._MV = 0.0
        self._SP = 0.0
        self._P = 8.0
        self._I = 5.0
        self._D = 2.0

    "método para atualização dos valores do PID"
    def update(self, medida):
        # Dados de sensores
        statusPID = medida['values']['StatusPID']
        if statusPID == 0:
            self.ids.statusPID.text = "Automático"
        elif statusPID == 1:
            self.ids.statusPID.text = "Manual"
        self.ids.cargaPV.text = str(medida['values']['CargaEsteira'])

        # Dados do PID
        medida['values']['TipoPID'] = 1  # Sempre Manual, problema no automático
        medida['values']['ControleP'] = self._P
        medida['values']['ControleI'] = self._I
        medida['values']['ControleD'] = self._D
        medida['values']['VarManip'] = self._MV
        medida['values']['SetPoint'] = self._SP

    def setP(self):
        self._P = float(self.ids.ControleP.text)

    def setI(self):
        self._I = float(self.ids.ControleI.text)

    def setD(self):
        self._D = float(self.ids.ControleD.text)

    def setSetPoint(self):
        self._SP = float(self.ids.SetPoint.text)

    def setMV(self):
        self._MV = float(self.ids.VarManip.text)

class HistGraphPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.get('tags').items():
            cb = LabeledCheckBoxHistGraph()
            cb.ids.label.text = key
            cb.id = key
            self.ids.sensores.add_widget(cb)

class LabeledCheckBoxHistGraph(BoxLayout):
    pass

"config de medições"
class MedicoesPopup(Popup):

    "construtor da classe"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    "método para atualização de valores de medições de grandezas elétricas"
    def update(self, medida):
        self.ids.CorrenteMedia.text = str(medida['values']['CorrenteMedia'])
        self.ids.FrequenciaRede.text = str(medida['values']['FrequenciaRede'])
        self.ids.PotAtivaTotal.text = str(medida['values']['PotAtivaTotal'])
        self.ids.tipoMotor.text = str(medida['values']['tipoMotor'])
        self.ids.PotAparenteTotal.text = str(medida['values']['PotAparenteTotal'])
        self.ids.PotReativaTotal.text = str(medida['values']['PotReativaTotal'])
        self.ids.dppRS.text = str(medida['values']['dppRS'])
        self.ids.dppST.text = str(medida['values']['dppST'])
        self.ids.dppTR.text = str(medida['values']['dppTR'])
        self.ids.CorrenteR.text = str(medida['values']['CorrenteR'])
        self.ids.CorrenteS.text = str(medida['values']['CorrenteS'])
        self.ids.CorrenteT.text = str(medida['values']['CorrenteT'])
        self.ids.THDCorrenteR.text = str(medida['values']['THDCorrenteR'])
        self.ids.THDCorrenteS.text = str(medida['values']['THDCorrenteS'])
        self.ids.THDCorrenteT.text = str(medida['values']['THDCorrenteT'])
    
        tipoMotor = medida['values']['tipoMotor']
        if tipoMotor == 1:
            self.ids.tipoMotor.text = str("Motor verde")
        elif tipoMotor == 2:
            self.ids.tipoMotor.text = str("Motor azul")

"config de medições de temperatura"
class TemperaturaPopup(Popup):

    "construtor da classe"
    def __init__(self, **kwargs):    
        super().__init__(**kwargs)
    
    "método para atualizar valores medidos"
    def update(self, medida):
        self.ids.TempCarc.text = str(medida['values']['TempCarc'])
        self.ids.tempR.text = str(medida['values']['tempR'])
        self.ids.tempS.text = str(medida['values']['tempS'])
        self.ids.tempT.text = str(medida['values']['tempT'])

"config de comandos do motor"
class ComandoPopup(Popup):
    _partida = None
    _operacao = None
    _velInversor = None
    _aceleracao = None
    _desaceleracao = None

    "construtor da classe"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._partida = "Inversor"  # Partida padrão -inversor
        self._operacao = 0  # Operação padrão -parado
        self._velInversor = float(self.ids.VelInv.text)
        self._aceleracao = float(self.ids.RampaAcelInv.text)
        self._desaceleracao = float(self.ids.RampaDesacelInv.text)

    def update(self, medida):
        medida['values']['PartidaDir'] = None

        medida['values']['PartidaST'] = None
        medida['values']['RampaAcelST'] = None
        medida['values']['RampaDesacelST'] = None

        medida['values']['PartidInv'] = None
        medida['values']['RampaAcelInv'] = None
        medida['values']['RampaDesacelInv'] = None
        medida['values']['VelInv'] = None

        if self._partida is not None:
            if self._partida == "Direta":
                medida['values']['PartidaDir'] = self._operacao
                medida['values']['TipoPartida'] = 3

            elif self._partida == "Soft-Start":
                medida['values']['PartidaST'] = self._operacao
                medida['values']['RampaAcelST'] = self._aceleracao
                medida['values']['RampaDesacelST'] = self._desaceleracao
                medida['values']['TipoPartida'] = 1

            elif self._partida == "Inversor":
                medida['values']['PartidInv'] = self._operacao
                medida['values']['RampaAcelInv'] = self._aceleracao
                medida['values']['RampaDesacelInv'] = self._desaceleracao
                medida['values']['VelInv'] = self._velInversor
                medida['values']['TipoPartida'] = 2

    def setPartida(self, partida):
        self._partida = partida

    def setOperacao(self, operacao):
        self._operacao = operacao

    def setAcc(self):
        self._aceleracao = float(self.ids.RampaAcelInv.text)

    def setDcc(self):
        self._desaceleracao = float(self.ids.RampaDesacelInv.text)

    def setVelInversor(self):
        self._velInversor = int(self.ids.VelInv.text)

    def setVelInversorSlider(self, vel):
        self._velInversor = vel

class SelectDataGraphPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)