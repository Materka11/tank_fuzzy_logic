import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class FuzzyController:
    def __init__(self):
        self.tank_capacity = 100
        self.natural_level = 30
        self.safe_level = 40
        self.warning_level = 60
        self.alarm_level = 75
        self.natural_tank = self.tank_capacity
        self.resistance_tank = 0
        self.pump_power = 100
        self.leak_rate = 0.2
        self.pump_active = True

    def triangular_membership(self, x, a, b, c):
        left_slope = (x - a) / (b - a) if a != b else 0
        right_slope = (c - x) / (c - b) if b != c else 0
        return max(min(left_slope, right_slope), 0)

    def fuzzify(self, level):
        low = self.triangular_membership(level, self.natural_level, self.safe_level, self.warning_level)
        medium = self.triangular_membership(level, self.safe_level, self.warning_level, self.alarm_level)
        high = self.triangular_membership(level, self.warning_level, self.alarm_level, self.tank_capacity)
        return {'low': low, 'medium': medium, 'high': high}

    def control_pump(self):
        if self.natural_tank <= self.safe_level:
            self.pump_active = False
        else:
            self.pump_active = True

        if self.pump_active:
            fuzzy_values = self.fuzzify(self.natural_tank)
            power_levels = {
                0: fuzzy_values['low'],
                50: fuzzy_values['medium'],
                100: fuzzy_values['high']
            }
            self.pump_power = self.defuzzify(power_levels)
        else:
            self.pump_power = 0

    def defuzzify(self, power_levels):
        numerator = sum(power * weight for power, weight in power_levels.items())
        denominator = sum(power_levels.values())
        return numerator / denominator if denominator != 0 else 0

    def update_tanks(self):
        flow = self.pump_power / 10
        dynamic_flow = min(flow, self.natural_tank - self.safe_level)
        self.natural_tank -= dynamic_flow + self.leak_rate
        self.resistance_tank = max(min(self.resistance_tank + dynamic_flow, self.tank_capacity), 0)
        self.natural_tank = max(self.natural_tank, self.natural_level)


class Application:
    def __init__(self):
        self.controller = FuzzyController()
        self.data_limit = 100

        # Inicjalizacja wykresu
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(6, 8), gridspec_kw={'hspace': 0.5})
        self.ax1.set_title("Poziom wody - Naturalny zbiornik")
        self.ax2.set_title("Moc pompy")
        self.ax3.set_title("Poziom wody - Zbiornik retencyjny")

        # Linie poziome dla poziomu naturalnego, alarmowego, ostrzegawczego i bezpiecznego
        self.line_alarm = self.ax1.axhline(y=self.controller.alarm_level, color='red', linestyle='--', label='Stan alarmowy')
        self.line_warning = self.ax1.axhline(y=self.controller.warning_level, color='orange', linestyle='--', label='Stan ostrzegawczy')
        self.line_safe = self.ax1.axhline(y=self.controller.safe_level, color='green', linestyle='--', label='Stan bezpieczny')
        self.line_natural = self.ax1.axhline(y=self.controller.natural_level, color='blue', linestyle='--', label='Stan naturalny')
                
        # Linie na wykresie dla danych
        self.water_data = []
        self.pump_power_data = []
        self.resistance_tank_data = []
        self.line1, = self.ax1.plot([], [], label="Naturalny zbiornik", color="blue")
        self.line2, = self.ax2.plot([], [], label="Moc pompy", color="red")
        self.line3, = self.ax3.plot([], [], label="Zbiornik retencyjny", color="green")

        # Ustawienia zakresu osi Y dla każdego wykresu
        self.ax1.set_ylim(-20, 120)
        self.ax2.set_ylim(-20, 120)
        self.ax3.set_ylim(-20, 120)

        # Inicjalizacja animacji
        self.ani = FuncAnimation(self.fig, self.update_simulation, interval=1000)

    def update_simulation(self, frame):
        # Uaktualnienie mocy pompy i poziomów wody
        self.controller.control_pump()
        self.controller.update_tanks()

        # Aktualizacja danych do wykresu
        self.water_data.append(self.controller.natural_tank)
        self.pump_power_data.append(self.controller.pump_power)
        self.resistance_tank_data.append(self.controller.resistance_tank)

        # Ograniczenie liczby punktów na wykresie
        if len(self.water_data) > self.data_limit:
            self.water_data.pop(0)
            self.pump_power_data.pop(0)
            self.resistance_tank_data.pop(0)

        # Aktualizacja legend z rzeczywistymi wartościami   
        line1, = self.ax1.plot([], [], label=f"Naturalny zbiornik: {self.controller.natural_tank:.2f}%", color="blue") 
        self.ax1.legend(handles=[self.line_alarm, self.line_warning, self.line_safe, self.line_natural, line1], loc="lower left") 
        self.ax2.legend([f"Moc pompy: {self.controller.pump_power:.2f}%"])
        self.ax3.legend([f"Zbiornik retencyjny: {self.controller.resistance_tank:.2f}%"])

        # Zaktualizuj wykresy
        self.update_plot()

    def update_plot(self):
        # Aktualizacja danych wykresu
        self.line1.set_data(range(len(self.water_data)), self.water_data)
        self.line2.set_data(range(len(self.pump_power_data)), self.pump_power_data)
        self.line3.set_data(range(len(self.resistance_tank_data)), self.resistance_tank_data)

        # Ograniczenie osi X do liczby punktów
        self.ax1.set_xlim(0, len(self.water_data))
        self.ax2.set_xlim(0, len(self.pump_power_data))
        self.ax3.set_xlim(0, len(self.resistance_tank_data))


# Uruchomienie aplikacji
app = Application()
plt.show()
