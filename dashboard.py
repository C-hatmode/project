import tkinter as tk

from tkinter import filedialog, messagebox

import pandas as pd

import numpy as np

import matplotlib.pyplot as plt

import seaborn as sns

from sklearn.decomposition import PCA

from sklearn.preprocessing import StandardScaler

import customtkinter as ctk

from reportlab.lib.pagesizes import letter

from reportlab.pdfgen import canvas

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import threading

import time

import os

class FraudDetection:

  def __init__(self):

    self.data = None

  def process_csv_file(self, file_path):

    try:

      df = pd.read_csv(file_path)

      if df.empty:

        return None, "Error: The uploaded CSV file is empty."

      df['Risk_Score'] = np.random.uniform(0, 1, df.shape[0])

      df['Fraudulent'] = df['Risk_Score'] > 0.75

      self.data = df

      return df, "CSV processed successfully!"

    except Exception as e:

      return None, f"Error processing CSV: {str(e)}"

class FraudDetectionGUI:

  def __init__(self, root):

    self.root = root

    self.root.title("Advanced Fraud Detection")

    self.root.geometry("1000x800")

    self.root.resizable(True, True)

    self.detector = FraudDetection()

    # Set initial theme

    ctk.set_appearance_mode("dark")

    ctk.set_default_color_theme("blue")

    # Main layout with sidebar

    self.sidebar = ctk.CTkFrame(self.root, width=250, corner_radius=0)

    self.sidebar.pack(side="left", fill="y")

    self.main_frame = ctk.CTkFrame(self.root, corner_radius=10)

    self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    # Sidebar content

    self.logo_label = ctk.CTkLabel(

      self.sidebar,

      text="FraudGuard",

      font=ctk.CTkFont(family="Helvetica", size=28, weight="bold"),

      text_color="#1E90FF"

    )

    self.logo_label.pack(pady=(30, 20))

    # Sidebar buttons

    button_style = {"width": 200, "height": 45, "corner_radius": 10, "font": ctk.CTkFont(size=14)}

    self.upload_btn = ctk.CTkButton(self.sidebar, text="📂 Load Data", command=self.upload_csv, **button_style)

    self.upload_btn.pack(pady=10)

    self.analyze_btn = ctk.CTkButton(self.sidebar, text="📊 Analyze", command=self.show_pca_plot, **button_style)

    self.analyze_btn.pack(pady=10)

    self.report_btn = ctk.CTkButton(self.sidebar, text="📄 Report", command=self.download_pdf_report, **button_style)

    self.report_btn.pack(pady=10)

    # Theme switch

    self.theme_switch = ctk.CTkSwitch(

      self.sidebar,

      text="Dark Mode",

      command=self.toggle_theme,

      font=ctk.CTkFont(size=12)

    )

    self.theme_switch.pack(pady=(50, 10))

    self.theme_switch.select() # Default to dark mode

    # Main frame content

    self.title_label = ctk.CTkLabel(

      self.main_frame,

      text="Transaction Analysis Dashboard",

      font=ctk.CTkFont(family="Helvetica", size=24, weight="bold")

    )

    self.title_label.pack(pady=(20, 10))

    # Stats frame

    self.stats_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")

    self.stats_frame.pack(fill="x", padx=20, pady=10)

    self.total_label = ctk.CTkLabel(self.stats_frame, text="Total: 0", font=ctk.CTkFont(size=14))

    self.total_label.grid(row=0, column=0, padx=20)

    self.fraud_label = ctk.CTkLabel(self.stats_frame, text="Fraud: 0 (0%)", font=ctk.CTkFont(size=14))

    self.fraud_label.grid(row=0, column=1, padx=20)

    # Progress bar

    self.progress = ctk.CTkProgressBar(self.main_frame, width=400)

    self.progress.pack(pady=10)

    self.progress.set(0)

    # Status label

    self.status_label = ctk.CTkLabel(

      self.main_frame,

      text="Ready to begin analysis...",

      font=ctk.CTkFont(size=14),

      text_color="#A0A0A0"

    )

    self.status_label.pack(pady=10)

    # Plot

    plt.style.use('dark_background')

    self.figure, self.ax = plt.subplots(figsize=(10, 6), dpi=100)

    self.canvas = FigureCanvasTkAgg(self.figure, master=self.main_frame)

    self.canvas_widget = self.canvas.get_tk_widget()

    self.canvas_widget.pack(fill="both", expand=True, padx=20, pady=10)

  def toggle_theme(self):

    mode = "dark" if self.theme_switch.get() else "light"

    ctk.set_appearance_mode(mode)

    plt.style.use('dark_background' if mode == "dark" else 'default')

    self.update_plot()

  def update_plot(self):

    if self.detector.data is not None:

      self.show_pca_plot()

  def upload_csv(self):

    def process_with_progress():

      self.progress.set(0)

      self.status_label.configure(text="⏳ Loading data...", text_color="#FFA500")

      file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

      if file_path:

        for i in range(10):

          self.progress.set(i/10)

          time.sleep(0.1) # Simulate processing

        df, message = self.detector.process_csv_file(file_path)

        self.progress.set(1)

        if df is not None:

          total = len(df)

          fraud = df["Fraudulent"].sum()

          fraud_pct = (fraud / total) * 100

          self.total_label.configure(text=f"Total: {total:,}")

          self.fraud_label.configure(text=f"Fraud: {fraud:,} ({fraud_pct:.1f}%)")

          self.status_label.configure(text="✅ Data Loaded!", text_color="#00FF00")

          messagebox.showinfo("Success", "Data processed successfully!")

        else:

          self.status_label.configure(text="❌ Load Failed", text_color="#FF0000")

          messagebox.showerror("Error", message)

        self.progress.set(0)

    threading.Thread(target=process_with_progress, daemon=True).start()

  def show_pca_plot(self):

    if self.detector.data is None:

      messagebox.showerror("Error", "Please load transaction data first!")

      return

    df = self.detector.data

    features = df.select_dtypes(include=[np.number]).drop(columns=["Risk_Score", "Fraudulent"], errors="ignore")

    if features.shape[1] < 2:

      messagebox.showerror("Error", "Insufficient numeric features for analysis!")

      return

    self.status_label.configure(text="⏳ Analyzing...", text_color="#FFA500")

    scaler = StandardScaler()

    scaled_data = scaler.fit_transform(features)

    pca = PCA(n_components=2)

    pca_result = pca.fit_transform(scaled_data)

    self.ax.clear()

    sns.scatterplot(

      x=pca_result[:, 0],

      y=pca_result[:, 1],

      hue=df["Fraudulent"],

      palette={True: "#FF5555", False: "#55FF55"},

      size=df["Fraudulent"].astype(int) * 20 + 40, # Make fraudulent points larger

      alpha=0.8,

      ax=self.ax

    )

    self.ax.set_title("Fraud Pattern Analysis", fontsize=18, pad=20)

    self.ax.set_xlabel("PC1", fontsize=12)

    self.ax.set_ylabel("PC2", fontsize=12)

    self.ax.legend(title="Status", labels=["Normal", "Fraud"], loc="upper right")

    self.ax.grid(True, linestyle='--', alpha=0.2)

    self.canvas.draw()

    self.status_label.configure(text="📈 Analysis Complete!", text_color="#00FF00")

  def download_pdf_report(self):

    if self.detector.data is None:

      messagebox.showerror("Error", "No data available for report!")

      return

    save_path = filedialog.asksaveasfilename(

      defaultextension=".pdf",

      filetypes=[("PDF Files", "*.pdf")],

      title="Save Fraud Report"

    )

    if save_path:

      self.status_label.configure(text="⏳ Generating report...", text_color="#FFA500")

      self.generate_pdf_report(save_path)

      self.status_label.configure(text="📜 Report Saved!", text_color="#00FF00")

      messagebox.showinfo("Success", "Report generated successfully!")

  def generate_pdf_report(self, save_path):

    c = canvas.Canvas(save_path, pagesize=letter)

    width, height = letter

    # Header

    c.setFillColorRGB(0, 0.2, 0.8)

    c.rect(0, height-80, width, 80, fill=True)

    c.setFillColorRGB(1, 1, 1)

    c.setFont("Helvetica-Bold", 24)

    c.drawCentredString(width/2, height-50, "Fraud Detection Report")

    # Stats

    c.setFillColorRGB(0, 0, 0)

    c.setFont("Helvetica", 12)

    total = len(self.detector.data)

    fraud = self.detector.data["Fraudulent"].sum()

    fraud_pct = (fraud / total) * 100

    stats = [

      f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",

      f"Total Transactions: {total:,}",

      f"Fraudulent: {fraud:,} ({fraud_pct:.2f}%)",

      f"Analysis Engine: FraudGuard v1.0"

    ]

    y_pos = height - 120

    for line in stats:

      c.drawString(50, y_pos, line)

      y_pos -= 20

    # Plot

    plot_path = "temp_plot.png"

    self.figure.savefig(plot_path, bbox_inches='tight', dpi=150)

    c.drawImage(plot_path, 50, 150, width=500, height=350)

    c.showPage()

    c.save()

    # Clean up the temporary file

    try:

      os.remove(plot_path)

    except:

      pass

if __name__ == "__main__":

  root = ctk.CTk()

  app = FraudDetectionGUI(root)

  root.mainloop()













































































