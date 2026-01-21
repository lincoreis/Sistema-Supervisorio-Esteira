from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import LinePlot
from timeseriesgraph import GRAPH_CONFIG

class ModbusPopup (Popup):
    """
    Popup configuração protocolo modbus
    """
    _info_lb = None
    def __init__(self, server_ip, server_port, **kwargs):
        """
        Construtor da classe ModbusPopup
        """
        super().__init__(**kwargs)
        self.ids.txt_ip.text = str(server_ip)
        self.ids.txt_port.text = str(server_port)

    def setInfo(self,message):
        self._info_lb = Label(text=message)
        self.ids.layout.add_widget(self._info_lb)

    def clearInfo(self):
        if self._info_lb is not None:
            self.ids.layout.remove_widget(self._info_lb)

class ScanPopup(Popup):
    """
    Popup configuração tempo de varredura
    """
    def __init__(self, scantime, **kwargs):
        """
        Construtor da classe ScanPopup
        """
        super().__init__(**kwargs)
        self.ids.txt_st.text = str(scantime)

class DataGraphPopup(Popup):
    def __init__(self, xmax, plot_color, **kwargs):
        super().__init__(**kwargs)
        # cria e adiciona um único plot ao gráfico
        self.plot = LinePlot(line_width=1.5, color=plot_color)
        self.ids.graph.add_plot(self.plot)
        self.ids.graph.xmax = xmax

        # grandeza padrão
        self.set_grandeza("VelocidadeEsteira")

    def set_grandeza(self, tag: str):
        cfg = GRAPH_CONFIG.get(tag)
        if cfg is None:
            print(f"[DataGraphPopup] Tag sem config no GRAPH_CONFIG: {tag}")
            return

        self._selected_tag = tag

        g = self.ids.graph
        # texto do eixo Y
        g.ylabel = f"{cfg['label']} ({cfg['unit']})"
        # limites
        g.ymin = cfg["ymin"]
        g.ymax = cfg["ymax"]

        # garante que os números da escala Y estão ativos
        g.y_grid_label = True

        # escolhe um passo de tick razoável
        span = cfg["ymax"] - cfg["ymin"]
        if span <= 20:
            g.y_ticks_major = 1
        elif span <= 200:
            g.y_ticks_major = 20
        elif span <= 1000:
            g.y_ticks_major = 100
        elif span <= 2000:
            g.y_ticks_major = 150
        else:
            g.y_ticks_major = 1000

        # limpa o gráfico (sem destruir os plots)
        try:
            g.clearGraph()
        except Exception as e:
            print("Erro ao limpar gráfico:", e)

class LabeledCheckBoxDataGraph(BoxLayout):
    pass

class PidPopup(Popup):
    """
    Popup para a configuração do PID
    """

    _SP = None
    _MV = None
    _P = None
    _I = None
    _D = None

    def __init__(self, **kwargs):
        """
        Construtor da classe PidPopup
        """
        super().__init__(**kwargs)
        # valores padrão
        self._MV = 0.0
        self._SP = 0.0
        self._P = 8.0
        self._I = 5.0
        self._D = 2.0

        # False = automático (padrão), True = manual
        self._modo_manual = False

    # MÉTODOS CHAMADOS PELO KV (AUTO / MANUAL)

    def setModoAutomatico(self):
        """Chamado quando o operador seleciona 'Automático' no popup."""
        self._modo_manual = False

    def setModoManual(self):
        """Chamado quando o operador seleciona 'Manual' no popup."""
        self._modo_manual = True

    # ATUALIZAÇÃO A CADA CICLO

    def update(self, medida: dict):
        """
        Atualiza textos do popup e prepara os valores para escrita no CLP.
        """
        values = medida["values"]

        # PV (carga da esteira) – id no KV é CargaEsteira
        try:
            pv = values.get("CargaEsteira", 0.0)
            self.ids.CargaEsteira.text = f"{pv:.2f} Kgf/cm²"
        except Exception:
            pass

        # Status na tela (com base no modo selecionado no popup)
        self.ids.statusPID.text = "Manual" if self._modo_manual else "Automático"

        # Parâmetros PID a serem enviados
        values["ControleP"] = self._P
        values["ControleI"] = self._I
        values["ControleD"] = self._D
        values["SetPoint"] = self._SP

        # TipoPID e MV dependendo do modo de operação
        if self._modo_manual:
            values["TipoPID"] = 1
            values["VarManip"] = self._MV   # em porcentagem (0–100)
        else:
            values["TipoPID"] = 0
            values["VarManip"] = None       # None = não escrever MV

    # SETTERS DOS CAMPOS NUMÉRICOS

    def setP(self):
        try:
            self._P = float(self.ids.ControleP.text.replace(",", "."))
        except ValueError:
            pass

    def setI(self):
        try:
            self._I = float(self.ids.ControleI.text.replace(",", "."))
        except ValueError:
            pass

    def setD(self):
        try:
            self._D = float(self.ids.ControleD.text.replace(",", "."))
        except ValueError:
            pass

    def setSetPoint(self):
        try:
            self._SP = float(self.ids.SetPoint.text.replace(",", "."))
        except ValueError:
            pass

    def setMV(self):
        """
        Lê MV digitado, limita entre 0 e 100 e atualiza o campo de texto.
        """
        try:
            mv = float(self.ids.VarManip.text.replace(",", "."))
        except ValueError:
            return

        if mv < 0:
            mv = 0.0
        elif mv > 100:
            mv = 100.0

        self._MV = mv
        self.ids.VarManip.text = f"{mv:.1f}"

class HistGraphPopup(Popup):
    def __init__(self, **kwargs):
        # dicionário de tags vem do MainWidget
        tags = kwargs.pop('tags', {})
        super().__init__(**kwargs)

        self._tags = tags  # guarda para usar cor etc.

        # Preenche os valores do Spinner com as tags disponíveis
        valores = list(tags.keys())
        self.ids.spn_grandeza.values = valores

        # define uma grandeza padrão
        if 'VelocidadeEsteira' in tags:
            default = 'VelocidadeEsteira'
        else:
            default = valores[0] if valores else ''

        if default:
            self.ids.spn_grandeza.text = default
            self.set_grandeza(default)

    def set_grandeza(self, tag: str):
        """Configura escala e rótulo do gráfico histórico para a grandeza escolhida."""
        cfg = GRAPH_CONFIG.get(tag)
        if cfg is None:
            print(f"[HistGraphPopup] Tag sem config no GRAPH_CONFIG: {tag}")
            return

        g = self.ids.graph
        g.ylabel = f"{cfg['label']} ({cfg['unit']})"
        g.ymin = cfg["ymin"]
        g.ymax = cfg["ymax"]
        g.y_grid_label = True

        # define passo dos ticks em função da faixa
        span = cfg["ymax"] - cfg["ymin"]
        if span <= 20:
            g.y_ticks_major = 1
        elif span <= 200:
            g.y_ticks_major = 20
        elif span <= 1000:
            g.y_ticks_major = 100
        else:
            g.y_ticks_major = 500

        # limpa o gráfico (sem apagar os plots)
        try:
            g.clearGraph()
        except Exception as e:
            print("Erro ao limpar gráfico histórico:", e)

class LabeledCheckBoxHistGraph(BoxLayout):
    pass

class MedicoesPopup(Popup):
    """
    Popup para a configuração das medições
    """

    def __init__(self, **kwargs):
        """
        Construtor da classe MedicoesPopup
        """
        super().__init__(**kwargs)
    
    def update(self, medida):
        """
        Método utilizado para atualizar os valores de medições de grandezas elétricas
        """
        values = medida["values"]
        
        self.ids.CorrenteMedia.text = str(values.get("CorrenteMedia", 0.0))
        self.ids.FrequenciaRede.text = str(values.get("FrequenciaRede", 0.0)/100)
        self.ids.PotAtivaTotal.text = str(values.get("PotAtivaTotal", 0.0))
        self.ids.PotAparenteTotal.text = str(values.get("PotAparenteTotal", 0.0))
        self.ids.PotReativaTotal.text = str(values.get("PotReativaTotal", 0.0))

        self.ids.dppRS.text = str(values.get("dppRS", 0.0)/10)
        self.ids.dppST.text = str(values.get("dppST", 0.0)/10)
        self.ids.dppTR.text = str(values.get("dppTR", 0.0)/10)

        self.ids.CorrenteR.text = str(values.get("CorrenteR", 0.0)/100)
        self.ids.CorrenteS.text = str(values.get("CorrenteS", 0.0)/100)
        self.ids.CorrenteT.text = str(values.get("CorrenteT", 0.0)/100)

        self.ids.THDCorrenteR.text = str(values.get("THDCorrenteR", 0.0)/10)
        self.ids.THDCorrenteS.text = str(values.get("THDCorrenteS", 0.0)/10)
        self.ids.THDCorrenteT.text = str(values.get("THDCorrenteT", 0.0)/10)
        
        Tipo_motor = int(values.get("TipoMotor", 0))
        if Tipo_motor == 1:
            self.ids.TipoMotor.text = "Motor verde"
        elif Tipo_motor == 2:
            self.ids.TipoMotor.text = "Motor azul"
        else:
            self.ids.TipoMotor.text = "-.-"

class TemperaturaPopup(Popup):
    """
    Popup para a configuração das medições de temperatura
    """

    def __init__(self, **kwargs):
        """
        Construtor da classe TemperaturaPopup
        """
        super().__init__(**kwargs)

    def update(self, medida):
        """
        Método utilizado para atualizar os valores das medições
        """
        values = medida["values"]

        self.ids.TempCarc.text = str(values.get("TempCarc", 0.0)/10)
        self.ids.tempR.text = str(values.get("tempR", 0.0)/10)
        self.ids.tempS.text = str(values.get("tempS", 0.0)/10)
        self.ids.tempT.text = str(values.get("tempT", 0.0)/10)

class ComandoPopup(Popup):
    """
    Popup para a configuração dos comandos do motor
    """

    _partida = None
    _operacao = None
    _velInversor = None
    _aceleracao = None
    _desaceleracao = None

    def __init__(self, **kwargs):
        """
        Construtor da classe ComandoPopup
        """
        super().__init__(**kwargs)
        self._partida = "Inversor"  # Partida padrão como inversor
        self._operacao = 0  # Operação padrão como parado
        self._velInversor = int(self.ids.VelInv.text)
        self._aceleracao = int(self.ids.RampaAcelInv.text)
        self._desaceleracao = int(self.ids.RampaDesacelInv.text)

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
        self._aceleracao = int(self.ids.RampaAcelInv.text)

    def setDcc(self):
        self._desaceleracao = int(self.ids.RampaDesacelInv.text)

    def setVelInversor(self):
        self._velInversor = int(self.ids.VelInv.text)

    def setVelInversorSlider(self, vel):
        self._velInversor = vel

class SelectDataGraphPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)