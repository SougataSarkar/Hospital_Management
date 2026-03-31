import tkcalendar
import tkinter as tk
from tkinter import messagebox, ttk
import csv, os
from tkcalendar import Calendar

FILE = "hospital_data.csv"
USER_FILE = "users.csv"

# ---------------- LOGIN ---------------- #

def register():
    role = role_var.get()
    username = user.get()
    password = pwd.get()
    if not username or not password:
        messagebox.showerror("Error", "Fields cannot be empty")
        return
    with open(USER_FILE, "a", newline="") as f:
        csv.writer(f).writerow([role, username, password])
    messagebox.showinfo("Success", f"Registered as {role}!")

def login():
    if not os.path.exists(USER_FILE):
        messagebox.showerror("Error", "No users found. Register first!")
        return

    with open(USER_FILE, "r") as f:
        for row in csv.reader(f):
            if len(row) < 3: continue
            if row[1] == user.get() and row[2] == pwd.get():
                open_dashboard(row[0])
                return

    messagebox.showerror("Error", "Invalid Login!")

# ---------------- DATE PICKER ---------------- #

def pick_date(entry):
    top = tk.Toplevel()
    top.title("Select Date")
    cal = Calendar(top, date_pattern="dd-mm-yyyy")
    cal.pack(padx=10, pady=10)

    def select():
        entry.delete(0, tk.END)
        entry.insert(0, cal.get_date())
        top.destroy()

    tk.Button(top, text="Select", command=select).pack(pady=5)

# ---------------- PRESCRIPTION ---------------- #

def generate_prescription():
    prescription.delete("1.0", tk.END)
    selected = table.selection()
    
    # Try to get data from table first, then from entries
    if selected:
        row_data = table.item(selected[0])['values']
        data = {
            "name": row_data[0], "id": row_data[1], "addr": row_data[2],
            "phone": row_data[3], "adm": row_data[4], "dis": row_data[5],
            "gen": row_data[6], "doc": row_data[7], "diag": row_data[8]
        }
    else:
        try:
            data = {
                "name": entries["Patient Name"].get(),
                "id": entries["Admission Id"].get(),
                "addr": entries["Address"].get(),
                "phone": entries["Phone No"].get(),
                "adm": entries["Admission Date"].get(),
                "dis": entries["Discharge Date"].get(),
                "gen": entries["Gender"].get(),
                "doc": entries["Doctor Assigned"].get(),
                "diag": entries["Diagnosis"].get()
            }
            if not all(data.values()):
                messagebox.showerror("Error", "Fill all fields or select a row!")
                return
        except KeyError as e:
            messagebox.showerror("Error", f"Field Error: {e}")
            return

    text = f"""
=========== HOSPITAL PRESCRIPTION ===========

Patient Name : {data['name']}
Admission ID : {data['id']}
Gender       : {data['gen']}

Diagnosis    : {data['diag']}
Doctor       : {data['doc']}

Address      : {data['addr']}
Phone No     : {data['phone']}

Admission    : {data['adm']}
Discharge    : {data['dis']}

---------------------------------------------
Doctor Signature: ___________________________
"""
    prescription.insert(tk.END, text)

# ---------------- DASHBOARD ---------------- #

def open_dashboard(role):
    root.withdraw()
    dash = tk.Toplevel()
    dash.geometry("1200x700")
    dash.title(f"Hospital Management System - {role}")

    tk.Label(dash, text="HOSPITAL MANAGEMENT SYSTEM",
             font=("Arial", 25, "bold"), fg="red").pack(fill="x", pady=10)

    main = tk.Frame(dash)
    main.pack(fill="both", expand=True)

    # FORM SECTION
    left = tk.LabelFrame(main, text="Patient Info")
    left.place(x=10, y=10, width=700, height=350)

    fields = [
        "Patient Name", "Admission Id", "Address", "Phone No",
        "Admission Date", "Discharge Date", "Gender",
        "Doctor Assigned", "Diagnosis"
    ]

    global entries
    entries = {}

    for i, field in enumerate(fields):
        tk.Label(left, text=field).grid(row=i, column=0, padx=10, pady=5, sticky="w")
        e = tk.Entry(left, width=30)
        e.grid(row=i, column=1, padx=10, pady=5)
        entries[field] = e
        if "Date" in field:
            tk.Button(left, text="📅", command=lambda ent=e: pick_date(ent)).grid(row=i, column=2)

    # PRESCRIPTION SECTION
    right = tk.LabelFrame(main, text="Prescription Output")
    right.place(x=720, y=10, width=450, height=350)
    global prescription
    prescription = tk.Text(right, font=("Courier", 10))
    prescription.pack(fill="both", expand=True, padx=5, pady=5)

    # BUTTONS
    btn_frame = tk.Frame(main)
    btn_frame.place(x=10, y=370)
    
    tk.Button(btn_frame, text="Add Record", width=12, command=add_record).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Update Record", width=12, command=update_record).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Delete Record", width=12, command=delete_record).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="Clear Fields", width=12, command=clear).grid(row=0, column=3, padx=5)
    tk.Button(btn_frame, text="Gen Prescription", width=15, bg="lightgreen", command=generate_prescription).grid(row=0, column=4, padx=5)
    tk.Button(btn_frame, text="Logout", width=12, bg="orange", command=lambda: logout(dash)).grid(row=0, column=5, padx=5)

    # TABLE SECTION
    table_frame = tk.Frame(main)
    table_frame.place(x=10, y=410, width=1170, height=250)
    
    global table
    columns = ("Name", "ID", "Address", "Phone", "Adm Date", "Dis Date", "Gender", "Doctor", "Diagnosis")
    table = ttk.Treeview(table_frame, columns=columns, show="headings")
    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=120)
    
    table.pack(side="left", fill="both", expand=True)
    sb = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
    table.configure(yscroll=sb.set)
    sb.pack(side="right", fill="y")

    load_table()

# ---------------- DATA FUNCTIONS ---------------- #

def add_record():
    data = [entries[f].get() for f in [
        "Patient Name", "Admission Id", "Address", "Phone No",
        "Admission Date", "Discharge Date", "Gender",
        "Doctor Assigned", "Diagnosis"
    ]]

    if any(item == "" for item in data):
        messagebox.showerror("Error", "All fields are required!")
        return

    with open(FILE, "a", newline="") as f:
        csv.writer(f).writerow(data)
    load_table()
    clear()

def load_table():
    table.delete(*table.get_children())
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            for row in csv.reader(f):
                if row: table.insert("", tk.END, values=row)

def delete_record():
    selected = table.selection()
    if not selected: return
    
    confirm = messagebox.askyesno("Confirm", "Delete selected record?")
    if confirm:
        idx = table.index(selected[0])
        data = []
        with open(FILE, "r") as f:
            data = list(csv.reader(f))
        
        if idx < len(data):
            del data[idx]
            with open(FILE, "w", newline="") as f:
                csv.writer(f).writerows(data)
            load_table()

def update_record():
    selected = table.selection()
    if not selected: return
    
    idx = table.index(selected[0])
    new_data = [entries[f].get() for f in [
        "Patient Name", "Admission Id", "Address", "Phone No",
        "Admission Date", "Discharge Date", "Gender",
        "Doctor Assigned", "Diagnosis"
    ]]

    data = []
    with open(FILE, "r") as f:
        data = list(csv.reader(f))
    
    data[idx] = new_data
    with open(FILE, "w", newline="") as f:
        csv.writer(f).writerows(data)
    load_table()

def clear():
    for e in entries.values():
        e.delete(0, tk.END)
    prescription.delete("1.0", tk.END)

def logout(win):
    win.destroy()
    root.deiconify()

# ---------------- MAIN LOGIN UI ---------------- #

root = tk.Tk()
root.geometry("450x400") # Slightly widened to accommodate labels
root.title("System Login")

frame = tk.Frame(root)
frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(frame, text="Hospital Login", font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

role_var = tk.StringVar(value="Staff")
tk.OptionMenu(frame, role_var, "Patient", "Staff").grid(row=1, column=0, columnspan=2, pady=5)

# Login ID Section
tk.Label(frame, text="Login Id:", font=("Arial", 10)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
user = tk.Entry(frame, font=("Arial", 10))
user.grid(row=2, column=1, pady=5)

# Password Section
tk.Label(frame, text="Password:", font=("Arial", 10)).grid(row=3, column=0, sticky="e", padx=5, pady=5)
pwd = tk.Entry(frame, font=("Arial", 10), show="*")
pwd.grid(row=3, column=1, pady=5)

tk.Button(frame, text="Login", width=15, command=login, bg="lightblue").grid(row=4, column=0, columnspan=2, pady=10)
tk.Button(frame, text="Register New User", width=15, command=register).grid(row=5, column=0, columnspan=2)

root.mainloop()
