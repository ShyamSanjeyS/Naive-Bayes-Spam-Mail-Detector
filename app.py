# app.py

import os
import csv
import webbrowser
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
from spam_classifier import SpamMailClassifier

import nltk
from nltk.tokenize import sent_tokenize

# ---------- Paths ----------
train_path = r"D:\Placements\projects\mail2\Naive_Bayes_Spam_Mail_Detector\Data\train-mails"
test_path = r"D:\Placements\projects\mail2\Naive_Bayes_Spam_Mail_Detector\Data\test-mails"
predictions_file = "predictions.csv"

# ---------- Summarizer ----------
def summarize_text(text, max_sentences=2):
    sentences = sent_tokenize(text)
    return " ".join(sentences[:max_sentences]) if len(sentences) > max_sentences else text

# ---------- Actions ----------
def classify_mail():
    content = email_input.get("1.0", tk.END).strip()
    if not content:
        messagebox.showwarning("Empty Input", "Please enter or load email content.")
        return

    try:
        model_type = model_type_var.get()
        classifier = SpamMailClassifier(train_path, test_path, model_type)
        classifier.train_and_evaluate()
        prediction = classifier.predict_text(content)

        result_label.config(text=f"Prediction: {prediction}")
        export_prediction(content, prediction)

        summary_output.delete("1.0", tk.END)
        summary_output.insert(tk.END, summarize_text(content))

    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_metrics():
    try:
        model_type = model_type_var.get()
        classifier = SpamMailClassifier(train_path, test_path, model_type)
        acc, matrix, report = classifier.train_and_evaluate()

        metrics_output.delete("1.0", tk.END)
        metrics_output.insert(tk.END, f"Accuracy: {acc:.4f}\n\nConfusion Matrix:\n{matrix}\n\nReport:\n{report}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r", encoding="latin1") as f:
            lines = f.readlines()
            email_input.delete("1.0", tk.END)
            email_input.insert(tk.END, "".join(lines[2:]))

def export_prediction(email_text, prediction):
    with open(predictions_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([email_text[:30] + "...", prediction])

def open_csv():
    abs_path = os.path.abspath(predictions_file)
    webbrowser.open(f'file:///{abs_path}')

def reset_predictions():
    if messagebox.askyesno("Confirm", "Are you sure you want to delete all predictions?"):
        with open(predictions_file, mode='w', newline='', encoding='utf-8') as file:
            csv.writer(file).writerow(["Email Preview", "Prediction"])
        messagebox.showinfo("Reset", "Predictions file reset successfully.")

def toggle_dark_mode():
    is_dark = dark_mode_var.get()
    bg = "#121212" if is_dark else "white"
    fg = "white" if is_dark else "black"
    app.configure(bg=bg)
    for widget in app.winfo_children():
        try:
            widget.configure(bg=bg, fg=fg)
        except:
            pass
    email_input.configure(bg=bg, fg=fg, insertbackground=fg)
    metrics_output.configure(bg=bg, fg=fg, insertbackground=fg)
    summary_output.configure(bg=bg, fg=fg, insertbackground=fg)

# ---------- GUI ----------
app = tk.Tk()
app.title("📧 Spam Mail Classifier")
app.geometry("800x850")
app.resizable(False, False)

style = ttk.Style()
style.theme_use('clam')

# ---------- Top Frame ----------
top_frame = tk.Frame(app)
top_frame.pack(pady=5)

tk.Label(top_frame, text="Model Type:", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(10, 5))
model_type_var = tk.StringVar(value="gaussian")
ttk.Combobox(top_frame, textvariable=model_type_var, values=["gaussian", "multinomial", "bernoulli"], width=15).pack(side=tk.LEFT)

dark_mode_var = tk.BooleanVar(value=False)
ttk.Checkbutton(top_frame, text="🌙 Dark Mode", variable=dark_mode_var, command=toggle_dark_mode).pack(side=tk.RIGHT, padx=10)

# ---------- Email Input ----------
tk.Label(app, text="📤 Enter or Load Email Content", font=("Segoe UI", 12, "bold")).pack(pady=(10, 3))
email_input = scrolledtext.ScrolledText(app, wrap=tk.WORD, height=8, font=("Consolas", 10))
email_input.pack(padx=15, pady=5, fill=tk.X)

# ---------- Buttons ----------
btn_frame = tk.Frame(app)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="📂 Load Email File", width=20, command=load_file, bg="#6C63FF", fg="white").pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="📤 Classify Email", width=20, command=classify_mail, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)

# ---------- Result ----------
result_label = tk.Label(app, text="Prediction: ", font=("Segoe UI", 13, "bold"), fg="#333")
result_label.pack(pady=10)

# ---------- Summary ----------
tk.Label(app, text="🧠 Auto Summary", font=("Segoe UI", 11, "bold")).pack()
summary_output = scrolledtext.ScrolledText(app, wrap=tk.WORD, height=4, font=("Segoe UI", 10))
summary_output.pack(padx=15, pady=5, fill=tk.X)

# ---------- Metrics ----------
tk.Button(app, text="📊 Show Evaluation Metrics", command=show_metrics, bg="#2196F3", fg="white").pack(pady=10)
metrics_output = scrolledtext.ScrolledText(app, wrap=tk.WORD, height=10, font=("Courier New", 10))
metrics_output.pack(padx=15, pady=5, fill=tk.BOTH)

# ---------- CSV Buttons ----------
csv_btn_frame = tk.Frame(app)
csv_btn_frame.pack(pady=10)

tk.Button(csv_btn_frame, text="📁 Open predictions.csv", command=open_csv, bg="#FF9800", fg="white", width=25).pack(side=tk.LEFT, padx=10)
tk.Button(csv_btn_frame, text="🧹 Reset predictions.csv", command=reset_predictions, bg="#F44336", fg="white", width=25).pack(side=tk.LEFT, padx=10)

# ---------- CSV Header ----------
if not os.path.exists(predictions_file):
    with open(predictions_file, mode='w', newline='', encoding='utf-8') as file:
        csv.writer(file).writerow(["Email Preview", "Prediction"])

# ---------- Mainloop ----------
app.mainloop()
