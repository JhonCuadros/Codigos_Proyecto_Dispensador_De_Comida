from machine import PWM, Pin
from time import ticks_ms, ticks_diff


class Alarma:
    def __init__(self, pin=13):
        self.audio = PWM(Pin(pin))
        self.audio.freq(2000)
        self.audio.duty_u16(0)

        # Melodia de aviso: notas ascendentes
        self.melodia_media = [
            (2093, 180), (2637, 180), (3136, 300), (0, 100)
        ]

        # Melodia de nivel bajo: patron mas urgente
        self.melodia_baja = [
            (3136, 120), (1760, 120), (3136, 120),
            (1760, 250), (0, 100)
        ]

        self.tipo = None
        self.melodia = []
        self.indice = 0
        self.inicio_nota = 0
        self.activa = False
        self.volumen = 0.0

    def calcular_volumen(self, nivel):
        if nivel >= 70:
            return 0.0
        elif nivel >= 30:
            return 0.20 + (70 - nivel) * 0.20 / 40
        else:
            return 0.40 + (30 - nivel) * 0.30 / 30

    def reproducir_nota(self):
        frecuencia, duracion = self.melodia[self.indice]
        if frecuencia == 0 or self.volumen <= 0:
            self.audio.duty_u16(0)
        else:
            self.audio.freq(frecuencia)
            duty = int(32768 * self.volumen)
            self.audio.duty_u16(min(32768, max(0, duty)))
        self.inicio_nota = ticks_ms()

    def iniciar_melodia(self, tipo):
        self.tipo = tipo
        self.indice = 0
        self.activa = True
        if tipo == "MEDIO":
            self.melodia = self.melodia_media
            print("AVISO: la comida empieza a escasear")
        else:
            self.melodia = self.melodia_baja
            print("ALERTA: queda poca comida")
        self.reproducir_nota()

    def detener(self):
        self.audio.duty_u16(0)
        self.activa = False
        self.tipo = None

    def actualizar(self, nivel, habilitada=True):
        if not habilitada or nivel >= 70:
            if self.activa:
                self.detener()
            return

        if nivel >= 30:
            nuevo_tipo = "MEDIO"
        else:
            nuevo_tipo = "BAJO"

        if nuevo_tipo != self.tipo:
            self.volumen = self.calcular_volumen(nivel)
            self.iniciar_melodia(nuevo_tipo)
            return

        self.volumen = self.calcular_volumen(nivel)

        if self.activa:
            frecuencia, duracion = self.melodia[self.indice]

            # Actualiza el ciclo util durante la nota actual.
            # Es una aproximacion de volumen; el timbre tambien puede cambiar.
            if frecuencia == 0 or self.volumen <= 0:
                self.audio.duty_u16(0)
            else:
                duty = int(32768 * self.volumen)
                self.audio.duty_u16(min(32768, max(0, duty)))

            # Avanza a la siguiente nota cuando termina su duracion.
            if ticks_diff(ticks_ms(), self.inicio_nota) >= duracion:
                self.indice += 1
                if self.indice >= len(self.melodia):
                    self.indice = 0
                self.reproducir_nota()
