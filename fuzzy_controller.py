import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation

class FuzzyController:
    def __init__(self):
        self.tank_capacity = 100  
        self.natural_tank = 70 
        self.resistance_tank = 0 
        self.pump_power = 0
        self.leak_rate = 0.05
        self.fill_rate = 0.5

    def triangular_membership(self, x, a, b, c):
        left_slope = (x - a) / (b - a) if a != b else 0
        right_slope = (c - x) / (c - b) if b != c else 0
        return max(min(left_slope, right_slope), 0)


    def fuzzify(self, level):
        low = self.triangular_membership(level, 0, 20, 40)
        medium = self.triangular_membership(level, 30, 50, 70)
        high = self.triangular_membership(level, 60, 80, 100)
        return {'low': low, 'medium': medium, 'high': high}

    def defuzzify(self, power_levels):
        numerator = sum(power * weight for power, weight in power_levels.items())
        denominator = sum(power_levels.values())
        return numerator / denominator if denominator != 0 else 0

    def control_pump(self):
        water_level = self.natural_tank
        fuzzy_values = self.fuzzify(water_level)

        power_levels = {
            0: fuzzy_values['low'],  
            50: fuzzy_values['medium'], 
            100: fuzzy_values['high'] 
        }

        self.pump_power = self.defuzzify(power_levels)

    def update_tanks(self):
         
        self.natural_tank = min(self.natural_tank + self.fill_rate, self.tank_capacity)
        
        transfer_rate = 1.0 
        amount_to_transfer = min(transfer_rate, self.natural_tank)
        self.natural_tank = max(self.natural_tank - amount_to_transfer, 0)
        self.resistance_tank = min(self.resistance_tank + amount_to_transfer, self.tank_capacity)

        self.natural_tank = max(self.natural_tank - self.leak_rate, 0)
        self.resistance_tank = max(self.resistance_tank - self.leak_rate, 0)

    def simulate(self, steps=80):
        self.natural_levels = []
        self.resistance_levels = []
        self.pump_powers = []

        for _ in range(steps):
            self.control_pump()
            self.update_tanks()

            self.natural_levels.append(self.natural_tank)
            self.resistance_levels.append(self.resistance_tank)
            self.pump_powers.append(self.pump_power)

        self.animate_results()

    def animate_results(self):
            fig, (ax1, ax2) = plt.subplots(2, 1)

            ax1.set_xlim(0, len(self.natural_levels))
            ax1.set_ylim(0, self.tank_capacity)
            ax1.set_xlabel('Czas (kroki)')
            ax1.set_ylabel('Poziom wody')
            natural_line, = ax1.plot([], [], color='blue', label='Naturalny zbiornik')
            resistance_line, = ax1.plot([], [], color='green', label='Rezystancyjny zbiornik')
            ax1.legend(loc='upper right')

            ax2.set_xlim(0, len(self.pump_powers))
            ax2.set_ylim(0, 100)
            ax2.set_xlabel('Czas (kroki)')
            ax2.set_ylabel('Moc pompki (%)')
            pump_line, = ax2.plot([], [], color='red', label='Moc pompki')
            ax2.legend(loc='upper right')

            def update(frame):
                natural_line.set_data(range(frame), self.natural_levels[:frame])
                resistance_line.set_data(range(frame), self.resistance_levels[:frame])

                pump_line.set_data(range(frame), self.pump_powers[:frame])

                return natural_line, resistance_line, pump_line

            ani = FuncAnimation(fig, update, frames=len(self.natural_levels), interval=100, blit=True)
            plt.tight_layout()
            plt.show()

controller = FuzzyController()
controller.simulate()
