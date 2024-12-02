import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np


class FuzzyController:
    def __init__(self):
        self.tank_capacity = 99
        self.natural_tank = 30  # Initial level
        self.additional_tank = 0  # Additional tank initial level
        self.additional_tank_capacity = 50  # Additional tank capacity
        self.leak_rate = 0.2
        self.pump_power = 0  # Initial pump power

        # Define fuzzy sets for input (tank level) and output (pump power)
        self.x_terms = {
            "A": (0, 0, 30),  # Adjust low range
            "B": (20, 50, 80),  # Adjust medium range
            "C": (60, 100, 100)  # Adjust high range
        }

        self.y_terms = {
            "D": (0, 10, 30),  # Adjust low pump power
            "E": (20, 50, 80),  # Adjust medium pump power
            "F": (60, 80, 100)  # Adjust high pump power
        }


        # Fuzzy rules
        self.rules = {
            "A": "D",
            "B": "E",
            "C": "F"
        }

    @staticmethod
    def triangular_membership(x, a, b, c):
        """Calculate the membership degree for a triangular function, handling edge cases."""
        left_slope = (x - a) / (b - a) if b != a else 0  # Avoid division by zero
        right_slope = (c - x) / (c - b) if c != b else 0  # Avoid division by zero
        return max(min(left_slope, right_slope), 0)

    def fuzzify(self, value, terms):
        memberships = {term: self.triangular_membership(value, *params) for term, params in terms.items()}
        print(f"[DEBUG] Tank Level: {value}, Membership Degrees: {memberships}")
        return memberships

    def inference(self, input_membership):
        output_membership = {term: 0 for term in self.y_terms}
        for input_term, output_term in self.rules.items():
            output_membership[output_term] = max(output_membership[output_term], input_membership[input_term])
        print(f"[DEBUG] Output Membership Degrees: {output_membership}")
        return output_membership

    def aggregate(self, output_membership):
        y_range = np.arange(0, 101, 1)
        aggregated = np.zeros_like(y_range, dtype=float)
        for term, membership in output_membership.items():
            a, b, c = self.y_terms[term]
            term_curve = np.maximum(
                np.minimum((y_range - a) / (b - a) if b != a else 0,
                        (c - y_range) / (c - b) if c != b else 0),
                0
            )
            aggregated = np.maximum(aggregated, np.minimum(term_curve, membership))

        print(f"[DEBUG] Aggregated Output (clean): {aggregated}")
        return y_range, aggregated



    def defuzzify(self, y, aggregated):
        """Defuzzify the aggregated fuzzy set using the center of gravity method."""
        numerator = np.nansum(y * aggregated)  # Use nansum to handle NaN safely
        denominator = np.nansum(aggregated)   # Use nansum to avoid NaN propagation

        if denominator == 0:  # Safeguard against invalid defuzzification
            print("[DEBUG] Denominator is zero during defuzzification. Returning 0 as default pump power.")
            return 0  # Default pump power when no meaningful output exists

        return numerator / denominator



    def control_pump(self):
        # Fuzzification
        input_membership = self.fuzzify(self.natural_tank, self.x_terms)

        # Inference
        output_membership = self.inference(input_membership)

        # Aggregation
        y, aggregated = self.aggregate(output_membership)

        # Defuzzification
        self.pump_power = self.defuzzify(y, aggregated)
        print(f"[DEBUG] Pump Power: {self.pump_power}")
        return y, aggregated, self.pump_power


    def update_tanks(self):
        """Update the tank levels based on pump output and leakage."""
        flow_rate = self.pump_power / 10
        excess_flow = max(0, self.natural_tank + flow_rate - self.tank_capacity)

        # Water flows to the additional tank if the natural tank is full
        self.natural_tank += flow_rate - excess_flow - self.leak_rate
        self.natural_tank = max(0, min(self.tank_capacity, self.natural_tank))

        self.additional_tank += excess_flow
        self.additional_tank = max(0, min(self.additional_tank_capacity, self.additional_tank))


class Application:
    def __init__(self):
        self.controller = FuzzyController()
        self.data_limit = 100

        # Initialize plots
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(6, 8))
        self.ax1.set_title("Tank Levels and Pump Power")
        self.ax2.set_title("Additional Tank Level")

        # Plot elements
        self.tank_levels, = self.ax1.plot([], [], label="Natural Tank", color="green")
        self.pump_power, = self.ax1.plot([], [], label="Pump Power", color="orange")
        self.additional_tank, = self.ax2.plot([], [], label="Additional Tank", color="blue")
        self.ax1.legend()
        self.ax1.grid()
        self.ax2.legend()
        self.ax2.grid()

        # Data storage
        self.tank_data = []
        self.power_data = []
        self.additional_tank_data = []

        # Animation
        self.ani = FuncAnimation(self.fig, self.update_simulation, interval=1000, blit=False)

    def update_simulation(self, frame):
        # Run the fuzzy controller
        y, aggregated, pump_power = self.controller.control_pump()

        # Update tanks
        self.controller.update_tanks()

        # Append data
        self.tank_data.append(self.controller.natural_tank)
        self.power_data.append(pump_power)
        self.additional_tank_data.append(self.controller.additional_tank)

        # Limit data to the last `data_limit` points
        if len(self.tank_data) > self.data_limit:
            self.tank_data.pop(0)
            self.power_data.pop(0)
            self.additional_tank_data.pop(0)

        # Update tank/pump plot
        x_data = range(len(self.tank_data))
        self.tank_levels.set_data(x_data, self.tank_data)
        self.pump_power.set_data(x_data, self.power_data)

        # Update additional tank plot
        self.additional_tank.set_data(x_data, self.additional_tank_data)

        # Rescale axes
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.ax2.relim()
        self.ax2.autoscale_view()

    def run(self):
        plt.show()


# Run the application
app = Application()
app.run()
