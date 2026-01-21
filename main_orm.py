from kivy.app import App
from mainwidget_dbrefactor import MainWidget
from kivy.lang.builder import Builder
from timeseriesgraph import TimeSeriesGraph


class MainApp(App):
    "Classe com o aplicativo, a classe MainApp é derivada da classe App"

    def build(self):
        "Método que gera o aplicativo com base no widget principal"

        self.widget = MainWidget(scan_time=1000, server_ip = 'localhost', server_port = 502, # VERIFICAR SEMPRE O IP
        modbus_addrs = {
            'VelocidadeEsteira':    {"addr":724, "tipo": "FP"},
            'FrequenciaRotacao':    {"addr": 884, "tipo": "FP"},
            'torque':   {"addr": 1420, "tipo": "FP"},
            'CargaEsteira':     {"addr": 710, "tipo": "FP"},
            'CorrenteMedia':    {"addr": 845, "tipo": "4x"},
            'FrequenciaRede':   {"addr": 830, "tipo": "4x"},
            'TempCarc':     {"addr": 706, "tipo": "FP"},
            'PotAtivaTotal':    {"addr": 855, "tipo": "4x"},
            'StatusPID':    {"addr": 722, "tipo": "4x"},
            'TipoMotor':    {"addr": 708, "tipo": "4x"},
            'IndicaPartida':    {"addr": 1216, "tipo": "4x"},
            'PotAparenteTotal':     {"addr": 863, "tipo": "4x"},
            'PotReativaTotal':  {"addr": 859, "tipo": "4x"},
            'dppRS':    {"addr": 847, "tipo": "4x"},
            'dppST':    {"addr": 848, "tipo": "4x"},
            'dppTR':    {"addr": 849, "tipo": "4x"},
            'CorrenteR':    {"addr": 840, "tipo": "4x"},
            'CorrenteS':    {"addr": 841, "tipo": "4x"},
            'CorrenteT':    {"addr": 842, "tipo": "4x"},
            'THDCorrenteR':     {"addr": 874, "tipo": "4x"},
            'THDCorrenteS':     {"addr": 875, "tipo": "4x"},
            'THDCorrenteT':     {"addr": 876, "tipo": "4x"},            
            'tempR':    {"addr": 700, "tipo": "FP"},
            'tempS':    {"addr": 702, "tipo": "FP"},
            'tempT':    {"addr": 704, "tipo": "FP"},
            'PartidInv':    {"addr": 1312, "tipo": "4x"},
            'PartidaST':    {"addr": 1316, "tipo": "4x"},
            'PartidaDir':   {"addr": 1319, "tipo": "4x"},
            'VelInv':   {"addr": 1313, "tipo": "4x"},
            'TipoPID':  {"addr": 1332, "tipo": "4x"},
            'TipoPartida':  {"addr": 1324, "tipo": "4x"},
            'ControleP':    {"addr": 1304, "tipo": "FP"},
            'ControleI':    {"addr": 1306, "tipo": "FP"},
            'ControleD':    {"addr": 1308, "tipo": "FP"},
            'SetPoint':     {"addr": 1302, "tipo": "FP"},
            'VarManip':     {"addr": 1310, "tipo": "FP"},
            'RampaAcelST':  {"addr": 1317, "tipo": "4x"},
            'RampaDesacelST':   {"addr": 1318, "tipo": "4x"},
            'RampaAcelInv':     {"addr": 1314, "tipo": "4x"},
            'RampaDesacelInv':  {"addr": 1315, "tipo": "4x"},
        },
        db_path = "C:\\Users\\linco\\OneDrive\\Área de Trabalho\\Esteira\\Esteira" #VERIFICAR SEMPRE O CAMINHO DA PASTA
        )
        return self.widget
    def on_stop(self):
        """
        Método executado quando a aplicação é fechada
        """
        self.widget.stopRefresh()
    

if __name__ == '__main__':
    Builder.load_string(open("mainwidget.kv",encoding='utf-8').read(),rulesonly=True)
    Builder.load_string(open("popups.kv",encoding='utf-8').read(),rulesonly=True)
    MainApp().run()