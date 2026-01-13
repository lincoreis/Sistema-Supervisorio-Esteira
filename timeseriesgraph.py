from kivy_garden.graph import Graph
from kivy.clock import Clock


"classe derivada para plotar gráficos temporais"
class TimeSeriesGraph(Graph):
    "construtor"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._trigger_time_label = Clock.create_trigger(self._addTimeLabels)
        self._timestamps = []
        self._max_points = kwargs.get("max_points")
        self._max_points = 20
        self._numMeds = 0
"método para atualização do eixo das abscissas com os valores das amostras"
if timestamps is not None:
            self._timestamps = timestamps
            if len(timestamps) >= 100:
                self.x_ticks_major = int(len(timestamps) / 10)
            else:
                self.x_ticks_major = 5
        self._trigger_time_label()

    "método para apagar os rótulos"
    def clearLabel(self, *args):
        for lb in self._x_grid_label:
            lb.text = ""

    "método para apagar os plots"
    def clearPlots(self):
        try:
            while len(self.plots) != 0:
                self.remove_plot(self.plots[0])
        except Exception as e:
            print(e.args)

    "método para atualizar o rótulo das abscissas"
    def _addTimeLabels(self, *args):
        try:
            labels = self._timestamps[0 : len(self._timestamps) : self.x_ticks_major]
            for i in range(0, min(len(self._x_grid_label), len(labels))):
                self._x_grid_label[i].text = str(labels[i].strftime("%H:%M:%S"))
        except Exception as e:
            print("Error: ", e.args)

    "método para limitar o máximo de pontos de um plot"
    def setMaxPoints(self, mp, plot_number):
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

    "método para atualizar os dados do gráfico"
    def updateGraph(self, meas, plot_number):
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

    "método para remover todos os pontos do gráfico"
    def clearGraph(self):
        self.clearPlots()  # Remove todas as curvas do gráfico