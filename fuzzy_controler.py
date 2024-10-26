import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import messagebox


class FuzzyController:
    def __init__(self):
        self.tank_capacity = 100
        self.natural_level = 30  # Poziom naturalny, początkowy poziom wody
        self.safe_level = 40     # Poziom bezpieczny
        self.warning_level = 60  # Poziom ostrzegawczy
        self.alarm_level = 75    # Poziom alarmowy
        self.natural_tank = self.natural_level  # Początkowy poziom w zbiorniku naturalnym
        self.resistance_tank = 0  # Domyślnie pusty
        self.pump_power = 0  # Domyślnie wyłączona pompa
        self.leak_rate = 0.2
        self.pump_active = False  # Pompa uruchamia się przy przekroczeniu poziomu ostrzegawczego

    def triangular_membership(self, x, a, b, c):
        left_slope = (x - a) / (b - a) if a != b else 0
        right_slope = (c - x) / (c - b) if b != c else 0
        return max(min(left_slope, right_slope), 0)

    def fuzzify(self, level):
        natural = self.triangular_membership(level, 0, 0, self.natural_level)
        low = self.triangular_membership(level, self.natural_level, self.safe_level, self.warning_level)
        medium = self.triangular_membership(level, self.safe_level, self.warning_level, self.alarm_level)
        high = self.triangular_membership(level, self.warning_level, self.alarm_level, self.tank_capacity)
        return {'natural': natural, 'low': low, 'medium': medium, 'high': high}

    def rain_effect(self, rain_intensity):
        # Wzrost poziomu wody w naturalnym zbiorniku w zależności od intensywności deszczu
        rain_increments = {
            0: 0.0,   # brak deszczu
            1: 0.2,   # mały deszcz
            2: 0.5,   # średni deszcz
            3: 1.0,   # duży deszcz
            4: 1.5    # ekstremalny deszcz
        }
        self.natural_tank += rain_increments.get(rain_intensity, 0)
        self.natural_tank = min(self.natural_tank, self.tank_capacity)  # Ograniczenie do maksymalnej pojemności

    def control_pump(self):
        # Uruchomienie pompy powyżej poziomu ostrzegawczego i wyłączenie przy poziomie bezpiecznym
        
        if self.natural_tank > self.warning_level:
            self.pump_active = True
            
        elif self.natural_tank <= self.safe_level:
            self.pump_active = False

        # Moc pompy zależy od poziomu wody, gdy pompa jest aktywna
        if self.pump_active:
            fuzzy_values = self.fuzzify(self.natural_tank)
            power_levels = {
                0: fuzzy_values['low'],       # Moc 0% dla poziomu niskiego (low)
                50: fuzzy_values['medium'],    # Moc 50% dla poziomu ostrzegawczego (medium)
                100: fuzzy_values['high']      # Moc 100% dla poziomu alarmowego (high)
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

        # Aktualizacja poziomu w zbiornikach - proporcjonalnie
        self.natural_tank -= dynamic_flow + self.leak_rate
        self.resistance_tank = max(min(self.resistance_tank + dynamic_flow, self.tank_capacity), 0)
        self.natural_tank = max(self.natural_tank, self.natural_level)  # Zapewnia minimalny poziom naturalny w zbiorniku


class Application:
    def __init__(self, root):
        self.controller = FuzzyController()
        self.data_limit = 100  # Maksymalna liczba punktów na wykresie

        # GUI - tytuł
        root.title("Symulacja zbiornika i pompy")

        # Intensywność deszczu
        tk.Label(root, text="Intensywność deszczu (0 - brak, 1 - mały, 2 - średni, 3 - duży, 4 - ekstremalny):").grid(row=0, column=0, padx=10, pady=10)
        self.rain_intensity_entry = tk.Entry(root)
        self.rain_intensity_entry.grid(row=0, column=1, padx=10, pady=10)

        # Wyniki
        tk.Label(root, text="Moc pompki:").grid(row=1, column=0, padx=10, pady=10)
        self.pump_power_label = tk.Label(root, text="0")
        self.pump_power_label.grid(row=1, column=1, padx=10, pady=10)

        # Wykres
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(6, 8))
        self.ax1.set_title("Poziom wody - Naturalny zbiornik")
        self.ax2.set_title("Moc pompki")
        self.ax3.set_title("Poziom wody - Zbiornik retencyjny")

        # Etykiety osi
        self.ax1.set_ylabel("Poziom wody [%]")
        self.ax2.set_ylabel("Moc pompki [%]")
        self.ax3.set_ylabel("Poziom wody [%]")
        self.ax3.set_xlabel("Czas (kroki)")

        # Linie poziome dla poziomu naturalnego, alarmowego, ostrzegawczego i bezpiecznego
        self.ax1.axhline(y=self.controller.alarm_level, color='red', linestyle='--', label='Stan alarmowy')
        self.ax1.axhline(y=self.controller.warning_level, color='orange', linestyle='--', label='Stan ostrzegawczy')
        self.ax1.axhline(y=self.controller.safe_level, color='green', linestyle='--', label='Stan bezpieczny')
        self.ax1.axhline(y=self.controller.natural_level, color='blue', linestyle='--', label='Stan naturalny')
        self.ax1.legend(loc="upper left")  # Przeniesienie legendy na lewą stronę

        # Linie na wykresie dla danych
        self.water_data = []
        self.pump_power_data = []
        self.resistance_tank_data = []
        self.line1, = self.ax1.plot([], [], label="Naturalny zbiornik", color="blue")
        self.line2, = self.ax2.plot([], [], label="Moc pompki", color="red")
        self.line3, = self.ax3.plot([], [], label="Zbiornik retencyjny", color="green")

        # Ustawienia zakresu osi Y dla każdego wykresu
        self.ax1.set_ylim(-20, 120)  # Zakres dla naturalnego zbiornika
        self.ax2.set_ylim(-20, 120)  # Zakres dla mocy pompy
        self.ax3.set_ylim(-20, 120)  # Zakres dla retencyjnego zbiornika

        # Inicjalizacja automatycznego odświeżania
        self.update_simulation()

    def update_simulation(self):
        try:
            # Pobranie dynamicznie intensywności deszczu od użytkownika
            rain_intensity = int(self.rain_intensity_entry.get()) if self.rain_intensity_entry.get() else 0

            # Uaktualnienie poziomu wody w naturalnym zbiorniku w zależności od deszczu
            self.controller.rain_effect(rain_intensity)

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

            # Wyświetlenie wyników
            self.pump_power_label.config(text=f"{self.controller.pump_power:.2f}")

            # Zaktualizuj wykresy
            self.update_plot()

        except ValueError:
            messagebox.showerror("Błąd", "Wprowadź poprawne wartości liczbowe.")

        # Kontynuacja dynamicznego odświeżania
        root.after(1000, self.update_simulation)  # Odświeżaj co 1 sekundę

    def update_plot(self):
        # Aktualizacja danych wykresu
        self.line1.set_data(range(len(self.water_data)), self.water_data)
        self.line2.set_data(range(len(self.pump_power_data)), self.pump_power_data)
        self.line3.set_data(range(len(self.resistance_tank_data)), self.resistance_tank_data)

        # Ograniczenie osi X do liczby punktów
        self.ax1.set_xlim(0, len(self.water_data))
        self.ax2.set_xlim(0, len(self.pump_power_data))
        self.ax3.set_xlim(0, len(self.resistance_tank_data))

        self.fig.canvas.draw()


# Uruchomienie interfejsu
root = tk.Tk()
app = Application(root)
plt.show()
root.mainloop()
