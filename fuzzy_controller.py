import matplotlib.pyplot as plt 


class FuzzyController:
    def __init__(self):
        # Parametry zbiornika
        self.tank_capacity = 100  # Maksymalna pojemność zbiorników
        self.natural_tank = 50  # Początkowy poziom w zbiorniku naturalnym
        self.resistance_tank = 100  # Początkowy poziom w zbiorniku rezystancyjnym
        self.pump_power = 0  # Moc pompy (0-100)

    def triangular_membership(self, x, a, b, c):
        # Unikamy dzielenia przez zero, jeśli a == b lub b == c
        left_slope = (x - a) / (b - a) if a != b else 0
        right_slope = (c - x) / (c - b) if b != c else 0
        return max(min(left_slope, right_slope), 0)


    def fuzzify(self, level):
        """Fuzzifikacja poziomu wody."""
        low = self.triangular_membership(level, 0, 0, 50)
        medium = self.triangular_membership(level, 25, 50, 75)
        high = self.triangular_membership(level, 50, 100, 100)
        return {'low': low, 'medium': medium, 'high': high}

    def defuzzify(self, power_levels):
        """Defuzzifikacja mocy pompy."""
        numerator = sum(power * weight for power, weight in power_levels.items())
        denominator = sum(power_levels.values())
        return numerator / denominator if denominator != 0 else 0

    def control_pump(self):
        """Główna logika sterowania pompą."""
        water_level = self.natural_tank
        fuzzy_values = self.fuzzify(water_level)

        # Reguły rozmyte
        power_levels = {
            0: fuzzy_values['high'],  # Jeśli poziom wody wysoki -> moc pompy 0
            50: fuzzy_values['medium'],  # Jeśli poziom wody średni -> moc pompy 50
            100: fuzzy_values['low']  # Jeśli poziom wody niski -> moc pompy 100
        }

        # Wyznaczamy nową moc pompy
        self.pump_power = self.defuzzify(power_levels)

    def update_tanks(self):
        """Aktualizacja poziomów wody w zbiornikach."""
        # Przepływ wody zgodnie z mocą pompy
        flow = self.pump_power / 10
        self.natural_tank = min(self.natural_tank + flow, self.tank_capacity)
        self.resistance_tank = max(self.resistance_tank - flow, 0)

    def simulate(self, steps=50):
        """Symulacja działania układu."""
        natural_levels = []
        pump_powers = []

        for _ in range(steps):
            self.control_pump()
            self.update_tanks()

            # Zapisujemy dane do wykresów
            natural_levels.append(self.natural_tank)
            pump_powers.append(self.pump_power)

        # Rysujemy wykresy
        self.plot_results(natural_levels, pump_powers)

    def plot_results(self, natural_levels, pump_powers):
        """Wykresy wyników."""
        fig, ax1 = plt.subplots()

        ax1.set_xlabel('Czas (kroki)')
        ax1.set_ylabel('Poziom wody (zbiornik naturalny)', color='tab:blue')
        ax1.plot(natural_levels, color='tab:blue', label='Poziom wody')
        ax1.tick_params(axis='y', labelcolor='tab:blue')

        ax2 = ax1.twinx()
        ax2.set_ylabel('Moc pompy', color='tab:red')
        ax2.plot(pump_powers, color='tab:red', label='Moc pompy')
        ax2.tick_params(axis='y', labelcolor='tab:red')

        fig.tight_layout()
        plt.title('Symulacja sterowania poziomem wody za pomocą logiki rozmytej')
        plt.show()

# Inicjalizacja kontrolera i symulacja
controller = FuzzyController()
controller.simulate()
