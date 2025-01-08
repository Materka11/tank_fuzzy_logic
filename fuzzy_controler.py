import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class WaterPumpGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("System zarządzania mocą pompy wodnej")

        # Poziomy zbiorników
        self.natural_reservoir_level = 100  # Poziom zbiornika naturalnego w %
        self.retention_reservoir_level = 0  # Poziom zbiornika retencyjnego w %
        self.pump_power = 100  # Moc pompy w %

        # Zmienna deszcz
        self.rain_intensity = "Brak"  # Brak, Lekki, Umiarkowany, Silny

        self.rain_rates = {
            "Brak": 0,          # No rain
            "Lekki": 0.3,       # Light rain
            "Umiarkowany": 0.7,   # Moderate rain
            "Silny": 1.2          # Heavy rain
        }

        # Stałe poziomy
        self.FULL_LEVEL = 100
        self.HIGH_LEVEL_MIN = 50
        self.HIGH_LEVEL_MAX = 100
        self.HIGH_LEVEL_MID1 = 75
        self.HIGH_LEVEL_MID2 = 50
        self.LOW_LEVEL_MAX = 50
        self.LOW_LEVEL_MIN = 20
        self.EMPTY_LEVEL_MAX = 30
        self.EMPTY_LEVEL_MIN = 10
        self.MEDIUM_LEVEL_MIN = 10
        self.MEDIUM_LEVEL_MAX = 100
        self.MEDIUM_LEVEL_MID1 = 30
        self.MEDIUM_LEVEL_MID2 = 50

        # Dane do wykresów
        self.time_steps = []
        self.natural_levels = []
        self.pump_powers = []
        self.retention_levels = []

        # Tworzenie elementów interfejsu
        self.create_widgets()
        self.update_simulation()

    def create_widgets(self):
        # Wykresy
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(8, 8))
        self.fig.tight_layout(pad=3)

        # Wykres poziomu zbiornika naturalnego
        self.ax1.set_title("Poziom Zbiornika Naturalnego (%)")
        self.ax1.set_ylim(0, 120)
        self.ax1.set_xlabel("Czas")
        self.ax1.set_ylabel("Poziom (%)")
        self.natural_line, = self.ax1.plot([], [], label="Naturalny", color='blue')

        # Linie pomocnicze dla poziomów
        self.ax1.axhline(self.HIGH_LEVEL_MAX, linestyle="--", color="purple", linewidth=1, label="Krytyczny")
        self.ax1.axhline(self.HIGH_LEVEL_MID1, linestyle="--", color="red", linewidth=1, label="Ostrzegawczy")
        self.ax1.axhline(self.HIGH_LEVEL_MID2, linestyle="--", color="green", linewidth=1, label="Bezpieczny")
        self.ax1.axhline(self.MEDIUM_LEVEL_MID1, linestyle="--", color="gray", linewidth=1, label="Niski")

        # Dodanie legendy
        self.ax1.legend(loc="lower left", fontsize="small", frameon=True)

        # Wykres mocy pompy
        self.ax2.set_title("Moc Pompy (%)")
        self.ax2.set_ylim(0, 120)
        self.ax2.set_xlabel("Czas")
        self.ax2.set_ylabel("Moc (%)")
        self.pump_line, = self.ax2.plot([], [], label="Pompa", color='green')

        # Wykres poziomu zbiornika retencyjnego
        self.ax3.set_title("Poziom Zbiornika Retencyjnego (%)")
        self.ax3.set_ylim(0, 120)
        self.ax3.set_xlabel("Czas")
        self.ax3.set_ylabel("Poziom (%)")
        self.retention_line, = self.ax3.plot([], [], label="Retencyjny", color='orange')

        # Osadzenie wykresów w interfejsie
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Przyciski sterujące
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.pause_button = ttk.Button(control_frame, text="Pauza", command=self.pause_simulation)
        self.pause_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.reset_button = ttk.Button(control_frame, text="Reset", command=self.reset_simulation)
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Dropdown for rain intensity
        self.rain_label = ttk.Label(control_frame, text="Deszcz:")
        self.rain_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.rain_var = tk.StringVar(value="Brak")
        self.rain_dropdown = ttk.Combobox(control_frame, textvariable=self.rain_var, values=["Brak", "Lekki", "Umiarkowany", "Silny"], state="readonly")
        self.rain_dropdown.pack(side=tk.LEFT, padx=5, pady=5)
        self.rain_dropdown.bind("<<ComboboxSelected>>", self.change_rain_intensity)


    def change_rain_intensity(self, event=None):
        self.rain_intensity = self.rain_var.get()

    def calculate_pump_power(self):
        # Funkcje przynależności
        def is_full(self, level):
            return 1 if level >= self.FULL_LEVEL else (level - 73) / 20 if level >= 73 else 0

        def is_high(self, level):
            if level <= self.HIGH_LEVEL_MIN or level >= self.HIGH_LEVEL_MAX:
                return 0
            elif level <= self.HIGH_LEVEL_MID1:
                return (level - self.HIGH_LEVEL_MIN) / (self.HIGH_LEVEL_MID1 - self.HIGH_LEVEL_MIN)
            else:
                return (self.HIGH_LEVEL_MAX - level) / (self.HIGH_LEVEL_MAX - self.HIGH_LEVEL_MID1)

        def is_low(self, level):
            return 1 if level <= self.LOW_LEVEL_MIN else (self.LOW_LEVEL_MAX - level) / (self.LOW_LEVEL_MAX - self.LOW_LEVEL_MIN) if level <= self.LOW_LEVEL_MAX else 0

        def is_empty(self, level):
            return 1 if level <= self.EMPTY_LEVEL_MIN else (self.EMPTY_LEVEL_MAX - level) / (self.EMPTY_LEVEL_MAX - self.EMPTY_LEVEL_MIN) if level <= self.EMPTY_LEVEL_MAX else 0

        def is_medium(self, level):
            if level <= self.MEDIUM_LEVEL_MIN or level >= self.MEDIUM_LEVEL_MAX:
                return 0
            elif level <= self.MEDIUM_LEVEL_MID1:
                return (level - self.MEDIUM_LEVEL_MIN) / (self.MEDIUM_LEVEL_MID1 - self.MEDIUM_LEVEL_MIN)
            elif level <= self.MEDIUM_LEVEL_MID2:
                return 1
            else:
                return (self.MEDIUM_LEVEL_MAX - level) / (self.MEDIUM_LEVEL_MAX - self.MEDIUM_LEVEL_MID2)

        # Stopnie przynależności
        natural_degrees = {
            "full": is_full(self, self.natural_reservoir_level),
            "high": is_high(self, self.natural_reservoir_level),
            "low": is_low(self, self.natural_reservoir_level),
        }
        retention_degrees = {
            "empty": is_empty(self, self.retention_reservoir_level),
            "medium": is_medium(self, self.retention_reservoir_level),
        }

        # Reguły sterujące
        rules = [
            {"if": min(natural_degrees["full"], retention_degrees["empty"]), "then": "high"},
            {"if": min(natural_degrees["full"], retention_degrees["medium"]), "then": "medium"},
            {"if": min(natural_degrees["high"], retention_degrees["empty"]), "then": "medium"},
            {"if": min(natural_degrees["high"], retention_degrees["medium"]), "then": "low"},
            {"if": min(natural_degrees["low"], retention_degrees["empty"]), "then": "low"},
        ]

        power_centroids = {
            "high": 100,
            "medium": 50,
            "low": 25,
        }

        numerator = 0
        denominator = 0
        for rule in rules:
            numerator += rule["if"] * power_centroids[rule["then"]]
            denominator += rule["if"]

        self.pump_power = numerator / denominator if denominator != 0 else 0

    def update_simulation(self):
        if hasattr(self, "running") and self.running:
            # Obliczenie mocy pompy
            self.calculate_pump_power()

            # Aktualizacja poziomów
            rain_rate = self.rain_rates[self.rain_intensity]
            self.natural_reservoir_level += rain_rate  # Deszcz zwiększa poziom zbiornika naturalnego

            transfer_rate = self.pump_power / 100 * 1.5
            self.natural_reservoir_level -= transfer_rate
            self.retention_reservoir_level += transfer_rate

            # Ograniczenia poziomów
            self.natural_reservoir_level = max(0, min(100, self.natural_reservoir_level))
            self.retention_reservoir_level = max(0, min(100, self.retention_reservoir_level))

            # Aktualizacja danych na wykresach
            self.time_steps.append(len(self.time_steps))
            self.natural_levels.append(self.natural_reservoir_level)
            self.pump_powers.append(self.pump_power)
            self.retention_levels.append(self.retention_reservoir_level)

            self.natural_line.set_data(self.time_steps, self.natural_levels)
            self.pump_line.set_data(self.time_steps, self.pump_powers)
            self.retention_line.set_data(self.time_steps, self.retention_levels)

            self.ax1.set_xlim(0, max(len(self.time_steps), 10))
            self.ax2.set_xlim(0, max(len(self.time_steps), 10))
            self.ax3.set_xlim(0, max(len(self.time_steps), 10))

            self.canvas.draw()

        self.root.after(100, self.update_simulation)

    def start_simulation(self):
        self.running = True

    def pause_simulation(self):
        self.running = False

    def reset_simulation(self):
        self.running = False
        self.natural_reservoir_level = 100
        self.retention_reservoir_level = 0
        self.pump_power = 100
        self.time_steps.clear()
        self.natural_levels.clear()
        self.pump_powers.clear()
        self.retention_levels.clear()
        self.natural_line.set_data([], [])
        self.pump_line.set_data([], [])
        self.retention_line.set_data([], [])
        self.canvas.draw()

# Uruchomienie aplikacji
root = tk.Tk()
app = WaterPumpGUI(root)
root.mainloop()
