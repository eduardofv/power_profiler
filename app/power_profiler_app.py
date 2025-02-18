import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from plotly.offline import plot
import os
from tkhtmlview import HTMLLabel

class CSVGrapherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Grapher with Plotly")
        self.filepath = None
        self.data = None
        self.figure_html = None

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # File selection button
        load_button = tk.Button(self.root, text="Load CSV", command=self.load_csv)
        load_button.pack(pady=10)

        # HTML Viewer for Plotly graph
        self.html_label = HTMLLabel(self.root, width=100, height=30)
        self.html_label.pack(padx=10, pady=10, fill="both", expand=True)

        # Area for sum calculation
        self.sum_label = tk.Label(self.root, text="Sum of selected area: 0.00 Watts", font=("Arial", 14))
        self.sum_label.pack(pady=10)

    def load_csv(self):
        # Open file dialog
        self.filepath = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("TXT Files", "*.txt")],
            title="Select a CSV File"
        )
        if not self.filepath:
            return  # User cancelled

        try:
            # Load CSV into pandas DataFrame
            self.data = pd.read_csv(
                    self.filepath, 
                    names=['millis', "dt", "v", "a", "watts","v_sh"],
                    on_bad_lines='skip'
                    )
            if not all(col in self.data.columns for col in ["millis", "watts"]):
                raise ValueError("CSV must contain 'millis' and 'watts' columns.")
            
            self.data['millis'] = pd.to_datetime(self.data['millis'], unit='ms')
            self.plot_data()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {e}")

    def plot_data(self):
        # Create Plotly figure
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Scatter(
            x=self.data['millis'],
            y=self.data['watts'],
            mode='lines',
            name='Watts'
        ))

        fig.update_layout(
            title="Watts vs. Time",
            xaxis_title="Time (millis)",
            yaxis_title="Watts",
            height=600,
            width=800
        )

        # Add JS callback to capture zoom events
        fig.update_layout(dragmode="zoom")
        fig["layout"]["on_update"] = """
        function (gd) {
            gd.on('plotly_relayout', function(eventData) {
                var xRange = eventData['xaxis.range'];
                if (xRange) {
                    const zoomStart = new Date(xRange[0]);
                    const zoomEnd = new Date(xRange[1]);
                    const data = JSON.parse(gd.data[0].customdata);
                    const filtered = data.filter(d => d[0] >= zoomStart && d[0] <= zoomEnd);
                    const sumWatts = filtered.reduce((acc, d) => acc + d[1], 0);
                    // Pass the sum to Tkinter
                    window.external.invoke(sumWatts);
                }
            });
        }
        """

        # Save figure to HTML and display in Tkinter
        self.figure_html = os.path.join(os.getcwd(), "plot.html")
        plot(fig, filename=self.figure_html, auto_open=False)

        with open(self.figure_html, "r") as file:
            html_content = file.read()
        self.html_label.set_html(html_content)

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = CSVGrapherApp(root)
    root.mainloop()

