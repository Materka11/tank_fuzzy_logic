# Water Pump Management System

## Overview

This project is a graphical user interface (GUI) application for managing the power of a water pump based on reservoir levels and rain intensity. The application uses Tkinter for the GUI and Matplotlib for visualizing reservoir levels and pump power over time.

## Features

+ Real-time simulation of water pump power and reservoir levels.

+ Dynamic rain intensity selection (None, Light, Moderate, Heavy).

+ Fuzzy logic-based pump control to regulate water levels.

+ Graphical visualization of the natural reservoir level, pump power, and retention reservoir level.

+ Control buttons for starting, pausing, and resetting the simulation.

## Technologies Used

+ Python

+ Tkinter (GUI framework)

+ Matplotlib (for plotting graphs)

## Installation

+ Clone the repository or download the script.

+ Ensure you have Python installed (>=3.6 recommended).

+ Install required dependencies using pip:

```
pip install matplotlib
```

+ Run the script:

```
python water_pump_gui.py
```

## How It Works

+ The natural reservoir starts at 100% and decreases as water is pumped out.

+ The retention reservoir starts at 0% and increases as it receives water from the natural reservoir.

+ Rain intensity affects how much water is added to the natural reservoir.

+ Fuzzy logic determines the pump power based on reservoir levels.

+ Graphs update dynamically to reflect real-time changes.

## Controls

+ Start: Begins the simulation.

+ Pause: Pauses the simulation.

+ Reset: Resets all parameters to their initial state.

+ Rain Dropdown: Allows selecting different rain intensities.

## Future Enhancements

+ Save simulation data for analysis.

+ Add user-defined reservoir capacity settings.

+ Improve fuzzy logic rules for better water management.

## License

This project is open-source and available for modification and use under the MIT License.
