from kivy_garden.graph import Graph
from kivy.clock import Clock

GRAPH_CONFIG = {
    "VelocidadeEsteira": {"label": "Velocidade da Esteira", "unit": "m/min", "ymin": 0, "ymax": 10},
    "FrequenciaRotacao": {"label": "Frequência de Rotação", "unit": "RPM", "ymin": 0, "ymax": 2000},
    "FrequenciaRede": {"label": "Frequência da Rede", "unit": "Hz", "ymin": 0, "ymax": 70},
    "Torque": {"label": "Torque", "unit": "N.m", "ymin": 0, "ymax": 100},
    "torque": {"label": "Torque", "unit": "N.m", "ymin": 0, "ymax": 100},


    "CorrenteR": {"label": "Corrente Fase R", "unit": "A", "ymin": 0, "ymax": 10},
    "CorrenteS": {"label": "Corrente Fase S", "unit": "A", "ymin": 0, "ymax": 10},
    "CorrenteT": {"label": "Corrente Fase T", "unit": "A", "ymin": 0, "ymax": 10},
    "CorrenteMedia": {"label": "Corrente Média", "unit": "A", "ymin": 0, "ymax": 10},

    "dppRS": {"label": "Tensão R-S", "unit": "V", "ymin": 0, "ymax": 300},
    "dppST": {"label": "Tensão S-T", "unit": "V", "ymin": 0, "ymax": 300},
    "dppTR": {"label": "Tensão T-R", "unit": "V", "ymin": 0, "ymax": 300},

    "PotAtivaTotal": {"label": "Potência Ativa", "unit": "W", "ymin": 0, "ymax": 10000},
    "PotReativaTotal": {"label": "Potência Reativa", "unit": "W", "ymin": 0, "ymax": 10000},
    "PotAparenteTotal": {"label": "Potência Aparente", "unit": "W", "ymin": 0, "ymax": 10000},

    "THDCorrenteR": {"label": "THD Corrente R", "unit": "%", "ymin": 0, "ymax": 300},
    "THDCorrenteS": {"label": "THD Corrente S", "unit": "%", "ymin": 0, "ymax": 300},
    "THDCorrenteT": {"label": "THD Corrente T", "unit": "%", "ymin": 0, "ymax": 300},

    "TempCarc": {"label": "Temp. Carcaça", "unit": "°C", "ymin": 0, "ymax": 120},
    "tempR": {"label": "Temp. Enrolamento R", "unit": "°C", "ymin": 0, "ymax": 120},
    "tempS": {"label": "Temp. Enrolamento S", "unit": "°C", "ymin": 0, "ymax": 120},
    "tempT": {"label": "Temp. Enrolamento T", "unit": "°C", "ymin": 0, "ymax": 120},
}

class TimeSeriesGraph(Graph):
    """
    Classe derivada que implementa a possibilidade de se plotar
    gráficos temporais
    """
    def __init__(self, **kwargs):
        """
        Construtor
        """
        super().__init__(**kwargs)
        self._trigger_time_label = Clock.create_trigger(self._addTimeLabels)
        self._timestamps = []
        self._max_points = kwargs.get("max_points")
        self._max_points = 20
        self._numMeds = 0

    def update_x_labels(self, timestamps=None):
        """
        Método para atualização do eixo das abscissas com os valores
        dos timestamps das amostras.

        :param timestamps: vetor com os timestamps. Se não for passado,
        usa o vetor interno, atualizado por updateGraph().
        """
        if timestamps is not None:
            self._timestamps = timestamps

            # Evitar poluição visual: no máx. ~6 rótulos no eixo X
            max_labels = 6
            n = len(timestamps)

            if n <= 1:
                # 0 ou 1 ponto -> deixa como 1 mesmo
                self.x_ticks_major = 1
            else:
                # passo mínimo para ter no máximo max_labels labels
                step = max(1, int(n / max_labels))
                self.x_ticks_major = step

        # dispara o callback que escreve os textos dos labels
        self._trigger_time_label()


    def clearLabel(self, *args):
        """
        Método que apaga os rótulos do eixo das abscissas
        """
        for lb in self._x_grid_label:
            lb.text = ""

    def clearPlots(self):
        """
        Método que apaga os plots do gráfico
        """
        try:
            while len(self.plots) != 0:
                self.remove_plot(self.plots[0])
        except Exception as e:
            print(e.args)

    def _addTimeLabels(self, *args):
        """
        Método privado utilizado para atualizar os rótulos do
        eixo das abscissas de acordo com o vetor de timestamps.
        Este método é invocado por meio do trigger _trigger_time_label
        """
        try:
            labels = self._timestamps[0 : len(self._timestamps) : self.x_ticks_major]
            for i in range(0, min(len(self._x_grid_label), len(labels))):
                self._x_grid_label[i].text = str(labels[i].strftime("%H:%M:%S"))
        except Exception as e:
            print("Error: ", e.args)

    def setMaxPoints(self, mp, plot_number):
        """
        Método utilizado para definir o número máximo de pontos de um
        determinado plot.
        :param mp: número máximo de pontos desejado
        :param plot_number: número do plot em que se deseja alterar o número
        de pontos
        """
        try:
            self._max_points = mp
            if mp == 100:
                self.x_ticks_major = 10
            else:
                self.x_ticks_major = 5
            if len(self.plots[plot_number].points) < self._max_points:
                self.xmax = (
                    min(self.plots[plot_number].points)[0] + self._max_points - 1
                )
            self.plots[plot_number].points = self.plots[plot_number].points[
                -self._max_points :
            ]
            self._timestamps = self._timestamps[-self._max_points :]
        except Exception as e:
            print(e.args)

    def updateGraph(self, meas, plot_number):
        """
        Método que atualiza os dados de um determinado gráfico
        :param meas: tupla com a medição no formato (datetime,valor)
        :param plot_number: número do plot que será atualizado
        """
        try:
            # Verifica se o número de pontos é maior que zero para atribuir corretamente o índice da medição
            self.plots[plot_number].points.append((self._numMeds, meas[1]))
            self._numMeds += 1

            self._timestamps.append(meas[0])
            self._timestamps = self._timestamps[-self._max_points :]

            # Verifica se o número de pontos é maior que o número máximo e remove os pontos mais antigos
            self.plots[plot_number].points = self.plots[plot_number].points[
                -self._max_points :
            ]

            # Atualiza o label da medição mais antiga
            self.xmin = min(self.plots[plot_number].points)[0]

            # Atualiza o label da medição mais recente
            if len(self.plots[plot_number].points) >= self._max_points:
                self.xmax = max(self.plots[plot_number].points)[0]
            else:
                Clock.schedule_once(self.clearLabel)

            self.update_x_labels()
        except Exception as e:
            print(e.args)

    def clearGraph(self):
        """
        Remove todos os pontos do gráfico sem remover as curvas.
        """
        try:
            # zera os pontos de todos os plots existentes
            for plot in self.plots:
                plot.points = []

            # zera os controles internos
            self._timestamps = []
            self._numMeds = 0

            # reseta eixo X
            self.xmin = 0
            if self._max_points:
                self.xmax = self._max_points - 1

            # limpa rótulos do eixo X
            self.clearLabel()
        except Exception as e:
            print("Erro clearGraph:", e)
