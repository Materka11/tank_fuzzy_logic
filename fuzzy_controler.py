import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

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

        # Define the terms for fuzzification
        self.x_terms = {
            "low": (self.natural_level, self.safe_level, self.warning_level),
            "medium": (self.safe_level, self.warning_level, self.alarm_level),
            "high": (self.warning_level, self.alarm_level, self.tank_capacity + 10)
        }
        
        self.y_terms = {
            "low": (0, 0, 50),
            "medium": (25, 50, 75),
            "high": (25, 50, 100),
            "low_medium": (0, 25, 50),  
            "medium_high": (25, 50, 100)
        }

        # Expanded rule base
        self.rules = {
            "low": ["low"],
            "medium": ["medium"],
            "high": ["high"],
            "low_medium": ["low", "medium"],
            "medium_high": ["medium", "high"]
        }

    def triangular_membership(self, x, a, b, c):
        """Calculates the membership degree for a triangular function."""
        left_slope = (x - a) / (b - a) if a != b else 0
        right_slope = (c - x) / (c - b) if b != c else 0
        membership_value = max(min(left_slope, right_slope), 0)
        print(f"[DEBUG] x={x}, a={a}, b={b}, c={c}, membership={membership_value}")
        return membership_value

    def fuzzify(self, value, terms):
        """Fuzzifies the input value into fuzzy sets."""
        memberships = {
            term: self.triangular_membership(value, *params)
            for term, params in terms.items()
        }
        print(f"[DEBUG] Fuzzify: {value} -> {memberships}")
        return memberships

    def inference(self, input_membership):
        """Performs inference based on the fuzzy rules."""
        output_membership = {term: 0 for term in self.y_terms}

        # Evaluate rules based on input membership
        for input_term, output_terms in self.rules.items():
            # Get the maximum membership value for the output terms
            max_membership = max(input_membership[input_term] for input_term in output_terms)
            for output_term in output_terms:
                output_membership[output_term] = max(output_membership[output_term], max_membership)

        print(f"[DEBUG] Inference: {output_membership}")
        return output_membership

    def aggregate(self, output_membership):
        """Aggregates the output fuzzy sets."""
        y = np.arange(0, 101, 1)  # Range for the output variable
        aggregated = np.zeros_like(y, dtype=float)

        for term, membership in output_membership.items():
            start, peak, end = self.y_terms[term]
            print(f"[DEBUG] Aggregating {term}: start={start}, peak={peak}, end={end}, membership={membership}")

            term_membership = np.maximum(
                np.minimum(
                    (y - start) / (peak - start) if peak != start else 0,
                    (end - y) / (end - peak) if end != peak else 0
                ),
                0
            )
            print(f"[DEBUG] Term membership: {term_membership}")
            aggregated = np.maximum(aggregated, np.minimum(term_membership, membership))

        print(f"[DEBUG] Aggregated result: {aggregated}")
        return y, aggregated

    def defuzzify(self, y, aggregated):
        """Defuzzifies the aggregated result using center of gravity."""
        numerator = np.sum(y * aggregated)
        denominator = np.sum(aggregated)
        result = numerator / denominator
        print(f"[DEBUG] Defuzzified pump power: {result}")
        return result

    def control_pump(self):
        """Controls the pump power based on fuzzy logic."""
        input_membership = self.fuzzify(self.natural_tank, self.x_terms)
        output_membership = self.inference(input_membership)
        y, aggregated = self.aggregate(output_membership)
        self.pump_power = self.defuzzify(y, aggregated)

    def update_tanks(self):
        """Updates the tank levels based on pump output and leakage."""
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

        # Linie na wykresie
        self.water_data = []
        self.pump_power_data = []
        self.resistance_tank_data = []
        self.line1, = self.ax1.plot([], [], label="Naturalny zbiornik", color="blue")
        self.line2, = self.ax2.plot([], [], label="Moc pompy", color="red")
        self.line3, = self.ax3.plot([], [], label="Zbiornik retencyjny", color="green")

        # Ustawienia zakresu osi Y
        self.ax1.set_ylim(-20, 120)
        self.ax2.set_ylim(-20, 120)
        self.ax3.set_ylim(-20, 120)

        # Inicjalizacja animacji
        self.ani = FuncAnimation(self.fig, self.update_simulation, interval=1000, save_count=100)

    def update_simulation(self, frame):
        """Symulacja aktualizacji zbiorników i sterowania pompą."""
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

        # Zaktualizuj wykresy
        self.update_plot()

    def update_plot(self):
        self.line1.set_data(range(len(self.water_data)), self.water_data)
        self.line2.set_data(range(len(self.pump_power_data)), self.pump_power_data)
        self.line3.set_data(range(len(self.resistance_tank_data)), self.resistance_tank_data)
        self.ax1.set_xlim(0, len(self.water_data))
        self.ax2.set_xlim(0, len(self.pump_power_data))
        self.ax3.set_xlim(0, len(self.resistance_tank_data))


# Uruchomienie aplikacji
app = Application()
plt.show()
