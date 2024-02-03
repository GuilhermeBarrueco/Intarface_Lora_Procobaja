#Feito por Guilherme Barrueco 2024
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import deque
import serial.tools.list_ports
import threading
from ttkthemes import ThemedStyle
from PIL import Image, ImageTk
import os


class InterfaceGrafica:
    def __init__(self, root):
        self.root = root
        self.root.title("Interface LoRa - PROCOBAJA")
        self.dados_buffer = deque(maxlen=50)  # Armazenar os últimos 50 pontos para o gráfico

       # Adicionar imagem no canto superior direito
        self.logo_image_right = Image.open("baja1.png")
        self.logo_image_right = self.logo_image_right.resize((350, 450))  # Ajuste o tamanho conforme necessário
        self.logo_photo_right = ImageTk.PhotoImage(self.logo_image_right)
        self.logo_label_right = tk.Label(root, image=self.logo_photo_right)
        self.logo_label_right.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        script_dir = os.path.dirname(__file__)
        self.nome_arquivo = os.path.join(script_dir, "dados_gravados.txt")

        # Utiliza o ThemedStyle
        self.style = ThemedStyle(root)
        self.style.set_theme("xpnative")  # Escolhe o tema, você pode experimentar diferentes temas

        # Criar variáveis de controle para os rótulos
        self.vel_var = tk.StringVar()
        self.rpm_var = tk.StringVar()
        self.nivel_var = tk.StringVar()
        self.bat_var = tk.StringVar()
        self.tcvt_var = tk.StringVar()
        self.tmot_var = tk.StringVar()

        # Configurar gráficos
        self.figura, ((self.eixo_vel, self.eixo_rpm), (self.eixo_tmot, self.eixo_tcvt)) = plt.subplots(nrows=2, ncols=2, figsize=(15, 5), dpi=100)
        self.figura.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

        self.linha_vel, = self.eixo_vel.plot([], [], label="Velocidade")
        self.eixo_vel.set_xlabel("Tempo")
        self.eixo_vel.set_ylabel("Velocidade")
        self.eixo_vel.legend()

        self.linha_rpm, = self.eixo_rpm.plot([], [], label="RPM", color='orange')
        self.eixo_rpm.set_xlabel("Tempo")
        self.eixo_rpm.set_ylabel("RPM")
        self.eixo_rpm.legend()

        self.linha_tmot, = self.eixo_tmot.plot([], [], label="TMOT", color='green')
        self.eixo_tmot.set_xlabel("Tempo")
        self.eixo_tmot.set_ylabel("TMOT")
        self.eixo_tmot.legend()

        self.linha_tcvt, = self.eixo_tcvt.plot([], [], label="TCVT", color='red')
        self.eixo_tcvt.set_xlabel("Tempo")
        self.eixo_tcvt.set_ylabel("TCVT")
        self.eixo_tcvt.legend()

        # Configurar barras horizontais
        self.figura_barras, (self.eixo_bat, self.eixo_nivel) = plt.subplots(nrows=1, ncols=2, figsize=(2, 1), dpi=100)

        self.barra_bat = self.eixo_bat.barh([0], [0], color='blue', height=0.2)
        self.eixo_bat.set_xlim(0, 12.6)
        self.eixo_bat.set_xlabel("Vbat (V)")
        self.eixo_bat.set_yticks([])

        self.barra_nivel = self.eixo_nivel.barh([0], [0], color='green', height=0.2)
        self.eixo_nivel.set_xlim(0, 100)
        self.eixo_nivel.set_xlabel("Nível de Combustível (%)")
        self.eixo_nivel.set_yticks([])

        # Ajuste vertical da altura dos eixos
        self.eixo_bat.set_position([0.1, 0.5, 0.4, 0.2])  # Ajuste os valores conforme necessário
        self.eixo_nivel.set_position([0.52, 0.5, 0.4, 0.2])  # Ajuste os valores conforme necessário

        # Configurar Canvas para as figuras
        self.canvas = FigureCanvasTkAgg(self.figura, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, rowspan=6, columnspan=1, padx=8, pady=5, sticky="nsew")

        self.canvas_barras = FigureCanvasTkAgg(self.figura_barras, master=root)
        self.canvas_widget_barras = self.canvas_barras.get_tk_widget()
        self.canvas_widget_barras.grid(row=6, column=0, rowspan=1, columnspan=1, padx=8, pady=1, sticky="nsew")

        # Configurar peso das linhas e colunas para expansão uniforme
        for i in range(5):
            self.root.grid_rowconfigure(i, weight=1)
            self.root.grid_columnconfigure(0, weight=1)

        frame_rotulos = ttk.Frame(root)
        frame_rotulos.grid(row=2, column=1, rowspan=1, padx=1, pady=2, sticky="w")

        rotulos = ["Velocidade", "RPM", "Nível", "Bateria", "TCVT", "TMOT"]
        unidades = ["Km/h", "RPM", "%", "V", "°C", "°C"]

        for i, (rotulo, unidade) in enumerate(zip(rotulos, unidades)):
            ttk.Label(frame_rotulos, text=f"{rotulo} ({unidade}):", font=("Arial", 20), foreground="red").grid(row=i, column=0,rowspan=1, columnspan=1, padx=1, pady=1, sticky="e")
            ttk.Label(frame_rotulos, textvariable=self.get_var(i), font=("Arial", 20), foreground="black").grid(row=i, column=1,rowspan=1, columnspan=1, padx=1, pady=1, sticky="w")

        # Caixa de seleção para as portas COM disponíveis
        self.ports = [port.device for port in serial.tools.list_ports.comports()]
        self.selected_port = tk.StringVar(value=self.ports[0])
        self.port_combobox = ttk.Combobox(root, textvariable=self.selected_port, values=self.ports, font=("Arial", 15))
        self.port_combobox.grid(row=5, column=1, padx=1, columnspan=1, rowspan = 1, pady=1, sticky="w")

        # Botões
        estilo_botao = ttk.Style()
        estilo_botao.configure("EstiloBotao.TButton", font=("Arial", 15), foreground="black", background="red", width=15, height=20)

        self.connect_button = ttk.Button(root, text="Conectar", command=self.conectar, style="EstiloBotao.TButton")
        self.connect_button.grid(row=6, column=1, padx=1, pady=1, sticky="w")

        self.disconnect_button = ttk.Button(root, text="Desconectar", command=self.desconectar, state=tk.DISABLED, style="EstiloBotao.TButton")
        self.disconnect_button.grid(row=6, column=1, padx=1, pady=1,columnspan=1, rowspan = 1, sticky="e")

        # Inicializar o processo de leitura dos dados (ainda não conectado)
        self.lendo_dados = False

    def get_var(self, index):
        # Retorna a variável apropriada com base no índice
        variaveis = [self.vel_var, self.rpm_var, self.nivel_var, self.bat_var, self.tcvt_var, self.tmot_var]
        return variaveis[index]

    def conectar(self):
        # Configurar a porta serial
        self.serial = serial.Serial(self.selected_port.get(), baudrate=115200)

        # Ativar/desativar botões
        self.connect_button.configure(state=tk.DISABLED)
        self.disconnect_button.configure(state=tk.NORMAL)

        # Iniciar o processo de leitura dos dados
        self.lendo_dados = True
        threading.Thread(target=self.ler_dados).start()

    def desconectar(self):
        # Parar o processo de leitura dos dados
        self.lendo_dados = False

        # Desativar/desativar botões
        self.connect_button.configure(state=tk.NORMAL)
        self.disconnect_button.configure(state=tk.DISABLED)

        # Fechar a porta serial
        if hasattr(self, 'serial') and self.serial.is_open:
            self.serial.close()

    def ler_dados(self):
        tempo = 0

        with open(self.nome_arquivo, "w") as arquivo:
            while self.lendo_dados:
                try:
                    # Ler uma linha da porta serial
                    linha = self.serial.readline().decode('utf-8', 'ignore').strip()
                    valores = [float(valor) for valor in linha.split(",")]

                    # Processar os dados da linha
                    vel, rpm, nivel, bat, tcvt, tmot = valores

                    # Atualizar as variáveis de controle
                    self.vel_var.set(f"{vel:2.0f}")
                    self.rpm_var.set(f"{rpm:4.0f}")
                    self.nivel_var.set(f"{nivel:3.0f}")
                    self.bat_var.set(f"{bat:2.1f}")
                    self.tcvt_var.set(f"{tcvt:3.1f}")
                    self.tmot_var.set(f"{tmot:3.1f}")

                    # Salvar os dados no arquivo
                    linha_arquivo = ",".join(map(str, (tempo, vel, rpm, tmot, tcvt, bat, nivel))) + "\n"
                    arquivo.write(linha_arquivo)
                    # Atualizar gráfico
                    self.dados_buffer.append((tempo, vel, rpm, tmot, tcvt))
                    self.atualizar_grafico()

                    # Atualizar barras horizontais
                    self.atualizar_barras(bat, nivel)

                    # Atualizar a interface gráfica
                    self.root.update()

                    tempo += 1  # Aumentar o tempo para cada ponto lido

                except Exception as e:
                    print(f"Erro ao processar dados: {e}")
                    # Adicione lógica adicional de tratamento de erro conforme necessário

    def atualizar_grafico(self):
        tempos, velocidades, rpms, tmots, tcvts = zip(*self.dados_buffer)
        self.linha_vel.set_data(tempos, velocidades)
        self.linha_rpm.set_data(tempos, rpms)
        self.linha_tmot.set_data(tempos, tmots)
        self.linha_tcvt.set_data(tempos, tcvts)

        self.eixo_vel.relim()
        self.eixo_rpm.relim()
        self.eixo_tmot.relim()
        self.eixo_tcvt.relim()

        self.eixo_vel.autoscale_view()
        self.eixo_rpm.autoscale_view()
        self.eixo_tmot.autoscale_view()
        self.eixo_tcvt.autoscale_view()

        self.canvas.draw()

    def atualizar_barras(self, bat, nivel):
        # Atualizar barras horizontais
        self.barra_bat[0].set_width(bat)
        self.barra_nivel[0].set_width(nivel)

        self.canvas_barras.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceGrafica(root)
    root.mainloop()
