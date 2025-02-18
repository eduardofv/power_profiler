import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class CSVGrapherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Grapher with Range Selection")
        self.data = None
        self.start_x = None  # Start of selection
        self.end_x = None  # End of selection
        self.fig = None
        self.ax = None
        self.canvas = None
        self.selected_area = None  # Keep track of the selected area
        self.cursor_start = None  # Cursor for start of selection
        self.cursor_end = None  # Cursor for end of selection

        self.press_cid = None  # Store connection IDs for event handling
        self.release_cid = None

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Load CSV button
        load_button = tk.Button(self.root, text="Load CSV", command=self.load_csv)
        load_button.pack(pady=10)

        # Clear Selection button
        clear_button = tk.Button(self.root, text="Clear Selection", command=self.clear_selection)
        clear_button.pack(pady=10)

        # Placeholder for Matplotlib canvas
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill="both", expand=True)

        # Integral display (instead of sum)
        self.integral_label = tk.Label(self.root, text="Integral of selected range: 0.00 Watts·ms", font=("Arial", 14))
        self.integral_label.pack(pady=10)

    def load_csv(self):
        # Open file dialog to select CSV
        filepath = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")], title="Select a CSV File"
        )
        if not filepath:
            return

        try:
            # Load CSV data into pandas DataFrame
            self.data = pd.read_csv(filepath)
            if not all(col in self.data.columns for col in ["millis", "watts"]):
                raise ValueError("CSV must contain 'millis' and 'watts' columns.")

            # Plot the data
            self.plot_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {e}")

    def plot_data(self):
        # Clear previous plot
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        # Create Matplotlib figure and axis
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.ax.plot(self.data["millis"], self.data["watts"], label="Watts")
        self.ax.set_title("Watts vs. Millis")
        self.ax.set_xlabel("Millis")
        self.ax.set_ylabel("Watts")
        self.ax.legend()

        # Define callback for button press (start selection)
        def on_press(event):
            if event.inaxes != self.ax:  # Ignore clicks outside the axes
                return
            self.start_x = event.xdata  # Record start of selection

            # Clear any existing cursor lines
            if self.cursor_start:
                self.cursor_start.remove()
            if self.cursor_end:
                self.cursor_end.remove()

            # Draw cursor line at the start of selection
            self.cursor_start = self.ax.axvline(x=self.start_x, color='red', linestyle='--')
            self.fig.canvas.draw()

        # Define callback for button release (end selection)
        def on_release(event):
            if event.inaxes != self.ax:  # Ignore clicks outside the axes
                return
            self.end_x = event.xdata  # Record end of selection
            if self.start_x is not None and self.end_x is not None:
                # Remove the cursor lines
                if self.cursor_start:
                    self.cursor_start.remove()
                if self.cursor_end:
                    self.cursor_end.remove()

                # Draw the cursor line at the end of selection
                self.cursor_end = self.ax.axvline(x=self.end_x, color='red', linestyle='--')

                # Remove previous selection if it exists
                if self.selected_area:
                    self.selected_area.remove()

                # Calculate the integral (area under the curve) in the selected range
                xmin, xmax = sorted([self.start_x, self.end_x])
                mask = (self.data["millis"] >= xmin) & (self.data["millis"] <= xmax)

                selected_data = self.data[mask]

                # Calculate the integral using trapezoidal rule
                integral = np.trapz(selected_data["watts"], selected_data["millis"])

                # Update the label with the integral value
                self.integral_label.config(text=f"Integral of selected range: {integral:.2f} Watts·ms")

                # Highlight selected range
                self.selected_area = self.ax.axvspan(xmin, xmax, color="blue", alpha=0.3)  # Highlight selected area
                self.fig.canvas.draw()  # Redraw the figure with highlighted area

        # Connect events for mouse selection
        self.press_cid = self.fig.canvas.mpl_connect('button_press_event', on_press)
        self.release_cid = self.fig.canvas.mpl_connect('button_release_event', on_release)

        # Embed the Matplotlib plot in the Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

        # Trigger the Matplotlib interactive event loop
        self.canvas.draw_idle()  # Ensures the plot is interactive
        self.canvas.draw()

    def clear_selection(self):
        # Clear the highlighted area and reset integral label
        if self.selected_area:
            self.selected_area.remove()  # Remove the highlighted range
            self.selected_area = None

        # Remove cursor lines if they exist
        if self.cursor_start and self.cursor_start in self.ax.lines:
            self.cursor_start.remove()  # Remove cursor line at start
            self.cursor_start = None

        if self.cursor_end and self.cursor_end in self.ax.lines:
            self.cursor_end.remove()  # Remove cursor line at end
            self.cursor_end = None

        # Redraw the plot
        self.fig.canvas.draw()

        # Reset the integral label
        self.integral_label.config(text="Integral of selected range: 0.00 Watts·ms")

        # Disconnect the events to reset the selection state
        self.fig.canvas.mpl_disconnect(self.press_cid)
        self.fig.canvas.mpl_disconnect(self.release_cid)

        # Reset the start and end selection variables
        self.start_x = None
        self.end_x = None

        # Re-enable selection by connecting the events again
        self.plot_data()  # Recreate the plot and event handlers

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = CSVGrapherApp(root)
    root.mainloop()

