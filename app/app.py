import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector

class CSVGrapherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Grapher with Range Selection")
        self.data = None

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Load CSV button
        load_button = tk.Button(self.root, text="Load CSV", command=self.load_csv)
        load_button.pack(pady=10)

        # Placeholder for Matplotlib canvas
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill="both", expand=True)

        # Sum display
        self.sum_label = tk.Label(self.root, text="Sum of selected range: 0.00 Watts", font=("Arial", 14))
        self.sum_label.pack(pady=10)

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
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(self.data["millis"], self.data["watts"], label="Watts")
        ax.set_title("Watts vs. Millis")
        ax.set_xlabel("Millis")
        ax.set_ylabel("Watts")
        ax.legend()

        # Define the callback for the range selection
        def on_select(xmin, xmax):
            # Mask the data to get the selected range
            mask = (self.data["millis"] >= xmin) & (self.data["millis"] <= xmax)
            selected_sum = self.data.loc[mask, "watts"].sum()  # Sum watts within the selected range
            self.sum_label.config(text=f"Sum of selected range: {selected_sum:.2f} Watts")

        # Create the SpanSelector to allow the user to select a range horizontally
        span = SpanSelector(
            ax,
            on_select,
            "horizontal",  # Selecting along the x-axis
            useblit=True,
            props=dict(alpha=0.5, facecolor="blue")  # Visual feedback of the selection
        )

        # Embed the Matplotlib plot in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)

        # Trigger the Matplotlib interactive event loop
        canvas.draw_idle()  # Ensures the plot is interactive

        # Update the Tkinter event loop
        canvas.draw()

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = CSVGrapherApp(root)
    root.mainloop()

