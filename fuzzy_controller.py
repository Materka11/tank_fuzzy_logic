import matplotlib.pyplot as plt 

class FuzzyController:
    def __init__(self):
        self.tank_capacity = 100  
        self.natural_tank = 50 
        self.resistance_tank = 100 
        self.pump_power = 0
        self.leak_rate = 0.2

    def triangular_membership(self, x, a, b, c):
        left_slope = (x - a) / (b - a) if a != b else 0
        right_slope = (c - x) / (c - b) if b != c else 0
        return max(min(left_slope, right_slope), 0)


    def fuzzify(self, level):
        low = self.triangular_membership(level, 0, 0, 50)
        medium = self.triangular_membership(level, 25, 50, 75)
        high = self.triangular_membership(level, 50, 100, 100)
        return {'low': low, 'medium': medium, 'high': high}

    def defuzzify(self, power_levels):
        numerator = sum(power * weight for power, weight in power_levels.items())
        denominator = sum(power_levels.values())
        return numerator / denominator if denominator != 0 else 0

    def control_pump(self):
        water_level = self.natural_tank
        fuzzy_values = self.fuzzify(water_level)

        power_levels = {
            0: fuzzy_values['high'],  
            50: fuzzy_values['medium'], 
            100: fuzzy_values['low'] 
        }

        self.pump_power = self.defuzzify(power_levels)

    def update_tanks(self):
        flow = self.pump_power / 10
        level_difference = self.natural_tank - self.resistance_tank
        dynamic_flow = flow + 0.05 * level_difference 

        self.natural_tank = min(
            self.natural_tank + dynamic_flow - self.leak_rate, self.tank_capacity
        )
        self.resistance_tank = max(self.resistance_tank - dynamic_flow, 0)

    def simulate(self, steps=60):
        natural_levels = []
        resistance_levels = []
        pump_powers = []

        for _ in range(steps):
            self.control_pump()
            self.update_tanks()

            natural_levels.append(self.natural_tank)
            resistance_levels.append(self.resistance_tank)
            pump_powers.append(self.pump_power)

        self.plot_results(natural_levels, resistance_levels, pump_powers)

    def plot_results(self, natural_levels, resistance_levels, pump_powers):
        fig, ax1 = plt.subplots(figsize=(10, 6))

        ax1.set_xlabel('Czas (kroki)')
        ax1.set_ylabel('Poziom wody (zbiornik naturalny)', color='tab:blue')
        ax1.plot(natural_levels, color='tab:blue', label='Poziom wody')
        ax1.tick_params(axis='y', labelcolor='tab:blue')

        ax2 = ax1.twinx()
        ax2.set_ylabel('Moc pompy', color='tab:red')
        ax2.plot(pump_powers, color='tab:red', linestyle='dashed', label='Moc pompy')
        ax2.tick_params(axis='y', labelcolor='tab:red')

        ax3 = ax1.twinx()
        ax3.spines.right.set_position(("outward", 60))  
        ax3.set_ylabel('Poziom wody (zbiornik rezystancyjny)', color='tab:green')
        ax3.plot(resistance_levels, color='tab:green', label='Poziom wody (rezystancyjny)')
        ax3.tick_params(axis='y', labelcolor='tab:green')

        fig.tight_layout()
        plt.title('Symulacja sterowania poziomem wody za pomocą logiki rozmytej')
        plt.show()

controller = FuzzyController()
controller.simulate()
