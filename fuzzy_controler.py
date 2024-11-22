import matplotlib.pyplot as plt  # Importuje bibliotekę do tworzenia wykresów.
from matplotlib.animation import FuncAnimation  # Importuje narzędzie do tworzenia animacji.
import numpy as np  # Importuje bibliotekę do operacji na danych numerycznych.

class FuzzyController:
    def __init__(self):  # Konstruktor klasy FuzzyController.
        # Parametry zbiornika
        self.tank_capacity = 100  # Pojemność zbiornika.
        self.natural_level = 30  # Naturalny poziom wody w zbiorniku.
        self.safe_level = 40  # Bezpieczny poziom wody w zbiorniku.
        self.warning_level = 60  # Ostrzegawczy poziom wody w zbiorniku.
        self.alarm_level = 75  # Alarmowy poziom wody w zbiorniku.
        self.natural_tank = self.tank_capacity  # Początkowy poziom wody w zbiorniku naturalnym.
        self.resistance_tank = 0  # Początkowy poziom wody w zbiorniku retencyjnym.
        self.pump_power = 100  # Moc pompy (0-100%).
        self.leak_rate = 0.2  # Stała szybkość wycieku wody.
        self.pump_active = True  # Stan działania pompy (True - aktywna, False - nieaktywna).

        # Zbiory rozmyte wejściowe i wyjściowe
        self.x_terms = {  # Definicja funkcji przynależności dla poziomu wody w zbiorniku.
            "low": (0, self.natural_level, self.safe_level),  # Funkcja przynależności "low".
            "medium": (self.safe_level, self.warning_level, self.alarm_level),  # Funkcja "medium".
            "high": (self.warning_level, self.alarm_level, self.tank_capacity + 10)  # Funkcja "high".
        }
        self.y_terms = {  # Definicja funkcji przynależności dla mocy pompy.
            "low": (0, 0, 50),  # Moc "low".
            "medium": (25, 50, 75),  # Moc "medium".
            "high": (50, 100, 150)  # Moc "high".
        }
        self.rules = {  # Reguły sterowania pompą.
            "low": "low",  # Jeśli poziom wody jest "low", to moc pompy jest "low".
            "medium": "medium",  # Jeśli poziom wody jest "medium", to moc jest "medium".
            "high": "high"  # Jeśli poziom wody jest "high", to moc jest "high".
        }

    def triangular_membership(self, x, a, b, c):  # Funkcja do obliczania przynależności do funkcji trójkątnej.
        left_slope = (x - a) / (b - a) if a != b else 0  # Wartość dla zbocza w lewo.
        right_slope = (c - x) / (c - b) if b != c else 0  # Wartość dla zbocza w prawo.
        return max(min(left_slope, right_slope), 0)  # Zwraca maksymalną przynależność.

    def fuzzify(self, value, terms):  # Funkcja rozmywania wartości wejściowej.
        memberships = {  # Oblicza przynależność dla każdego termu.
            term: self.triangular_membership(value, *params)
            for term, params in terms.items()
        }
        print(f"[DEBUG] Fuzzify: {value} -> {memberships}")  # Debug: wyświetla przynależności.
        return memberships

    def inference(self, input_membership):  # Funkcja wnioskowania na podstawie reguł.
        output_membership = {term: 0 for term in self.y_terms}  # Inicjalizuje przynależności wyjściowe.
        for input_term, output_term in self.rules.items():  # Iteruje po regułach.
            output_membership[output_term] = max(output_membership[output_term], input_membership[input_term])  # Maksymalna wartość przynależności.
        print(f"[DEBUG] Inference: {output_membership}")  # Debug: wyświetla wynik wnioskowania.
        return output_membership

    def aggregate(self, output_membership):  # Funkcja agregacji przynależności wyjściowych.
        y = np.arange(0, 101, 1)  # Zakres zmiennej wyjściowej (0-100).
        aggregated = np.zeros_like(y, dtype=float)  # Inicjalizacja tablicy wynikowej.
        for term, membership in output_membership.items():  # Iteruje po termach wyjściowych.
            start, peak, end = self.y_terms[term]  # Pobiera zakres funkcji przynależności.
            print(f"[DEBUG] Aggregating {term}: start={start}, peak={peak}, end={end}, membership={membership}")
            term_membership = np.maximum(
                np.minimum(
                    (y - start) / (peak - start) if peak != start else 0,
                    (end - y) / (end - peak) if end != peak else 0
                ),
                0
            )  # Oblicza przynależność dla zakresu `y`.
            aggregated = np.maximum(aggregated, np.minimum(term_membership, membership))  # Łączy przynależności.
        print(f"[DEBUG] Aggregated result: {aggregated}")  # Debug: wyświetla wynik agregacji.
        return y, aggregated

    def defuzzify(self, y, aggregated):  # Funkcja wyostrzania (defuzzification).
        numerator = np.sum(y * aggregated)  # Licznik: suma iloczynów `y` i przynależności.
        denominator = np.sum(aggregated)  # Mianownik: suma przynależności.
        result = numerator / denominator if denominator != 0 else 0  # Wyznacza środek ciężkości.
        print(f"[DEBUG] Defuzzified pump power: {result}")  # Debug: wyświetla moc pompy.
        return result

    def control_pump(self):  # Funkcja sterowania pompą.
        input_membership = self.fuzzify(self.natural_tank, self.x_terms)  # Rozmywanie poziomu wody.
        output_membership = self.inference(input_membership)  # Wnioskowanie na podstawie reguł.
        y, aggregated = self.aggregate(output_membership)  # Agregacja wyników wnioskowania.
        self.pump_power = self.defuzzify(y, aggregated)  # Wyostrzanie i aktualizacja mocy pompy.

    def update_tanks(self):  # Funkcja aktualizująca poziomy w zbiornikach.
        flow = self.pump_power / 10  # Oblicza przepływ na podstawie mocy pompy.
        dynamic_flow = min(flow, self.natural_tank - self.safe_level)  # Ogranicza przepływ do poziomu wody.
        self.natural_tank -= dynamic_flow + self.leak_rate  # Aktualizuje poziom wody w zbiorniku naturalnym.
        self.resistance_tank = max(min(self.resistance_tank + dynamic_flow, self.tank_capacity), 0)  # Aktualizuje zbiornik retencyjny.
        self.natural_tank = max(self.natural_tank, self.natural_level)  # Utrzymuje minimalny poziom wody.

class Application:
    def __init__(self):  # Konstruktor klasy Application.
        self.controller = FuzzyController()  # Tworzy instancję kontrolera rozmytego.
        self.data_limit = 100  # Limit danych na wykresie.

        # Inicjalizacja wykresu
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(6, 8), gridspec_kw={'hspace': 0.5})  # Tworzy wykres.
        self.ax1.set_title("Poziom wody - Naturalny zbiornik")  # Tytuł wykresu 1.
        self.ax2.set_title("Moc pompy")  # Tytuł wykresu 2.
        self.ax3.set_title("Poziom wody - Zbiornik retencyjny")  # Tytuł wykresu 3.

        # Linie na wykresie
        self.water_data = []  # Dane poziomu wody w zbiorniku naturalnym.
        self.pump_power_data = []  # Dane mocy pompy.
        self.resistance_tank_data = []  # Dane poziomu w zbiorniku retencyjnym.
        self.line1, = self.ax1.plot([], [], label="Naturalny zbiornik", color="blue")  # Linia wykresu 1.
        self.line2, = self.ax2.plot([], [], label="Moc pompy", color="red")  # Linia wykresu 2.
        self.line3, = self.ax3.plot([], [], label="Zbiornik retencyjny", color="green")  # Linia wykresu 3.

        # Ustawienia zakresu osi Y
        self.ax1.set_ylim(-20, 120)  # Zakres dla osi Y wykresu 1.
        self.ax2.set_ylim(-20, 120)  # Zakres dla osi Y wykresu 2.
        self.ax3.set_ylim(-20, 120)  # Zakres dla osi Y wykresu 3.

        # Inicjalizacja animacji
        self.ani = FuncAnimation(self.fig, self.update_simulation, interval=1000, save_count=100)  # Tworzy animację.

    def update_simulation(self, frame):  # Aktualizuje dane i symulację.
        self.controller.control_pump()  # Sterowanie pompą.
        self.controller.update_tanks()  # Aktualizacja poziomów w zbiornikach.

        # Aktualizacja danych do wykresu
        self.water_data.append(self.controller.natural_tank)  # Dodaje dane zbiornika naturalnego.
        self.pump_power_data.append(self.controller.pump_power)  # Dodaje dane mocy pompy.
        self.resistance_tank_data.append(self.controller.resistance_tank)  # Dodaje dane zbiornika retencyjnego.

        # Ograniczenie liczby punktów na wykresie
        if len(self.water_data) > self.data_limit:
            self.water_data.pop(0)
            self.pump_power_data.pop(0)
            self.resistance_tank_data.pop(0)

        # Zaktualizuj wykresy
        self.update_plot()

    def update_plot(self):  # Aktualizuje linie wykresu.
        self.line1.set_data(range(len(self.water_data)), self.water_data)
        self.line2.set_data(range(len(self.pump_power_data)), self.pump_power_data)
        self.line3.set_data(range(len(self.resistance_tank_data)), self.resistance_tank_data)
        self.ax1.set_xlim(0, len(self.water_data))  # Ustawia zakres osi X.
        self.ax2.set_xlim(0, len(self.pump_power_data))
        self.ax3.set_xlim(0, len(self.resistance_tank_data))


# Uruchomienie aplikacji
app = Application()  # Tworzy instancję aplikacji.
plt.show()  # Wyświetla wykresy i animację.
