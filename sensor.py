from machine import ADC, Pin
from time import sleep_ms


class SensorComida:

    def __init__(self, pin=34, alfa=0.20):
        self.sensor = ADC(Pin(pin))
        self.sensor.atten(ADC.ATTN_11DB)

        # Configuracion del filtro EMA
        self.alfa = alfa
        self.filtrado = None

    # Lee varias muestras y calcula el promedio
    def leer_adc(self, muestras=20):
        total = 0

        for _ in range(muestras):
            total += self.sensor.read()
            sleep_ms(10)

        return total / muestras

    # Aplica el filtro EMA al promedio obtenido
    def leer_adc_filtrado(self):
        lectura = self.leer_adc()

        # Primera lectura: inicializa el filtro
        if self.filtrado is None:
            self.filtrado = lectura
        else:
            # Ecuacion del filtro EMA
            self.filtrado = (
                self.alfa * lectura
                + (1 - self.alfa) * self.filtrado
            )

        return self.filtrado

    # Convierte el valor ADC en distancia aproximada
    def calcular_distancia(self, valor):

        if valor >= 2660:
            return 10

        elif valor >= 1270:
            return 10 + (
                (valor - 2660) * 10
                / (1270 - 2660)
            )

        elif valor >= 850:
            return 20 + (
                (valor - 1270) * 10
                / (850 - 1270)
            )

        elif valor >= 575:
            return 30 + (
                (valor - 850) * 10
                / (575 - 850)
            )

        else:
            return 40

    # Calcula el porcentaje estimado de comida
    def calcular_nivel(self, distancia):
        nivel = ((40 - distancia) / 30) * 100

        # Limita el resultado al rango de 0 a 100 %
        return max(0, min(100, nivel))

    # Obtiene los valores del sensor y aplica el EMA
    def obtener_nivel(self):
        valor_adc = self.leer_adc_filtrado()

        distancia = self.calcular_distancia(valor_adc)

        nivel = self.calcular_nivel(distancia)

        return valor_adc, distancia, nivel
