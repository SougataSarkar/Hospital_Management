import tkinter as tk
from tkinter import messagebox, ttk
import csv, os
from tkcalendar import Calendar

FILE = "hospital_data.csv"
USER_FILE = "users.csv"

# ---------------- LOGIN ---------------- #

def register():
    with open(USER_FILE, "a", newline="") as f:
        csv.writer(f).writerow([role_var.get(), user.get(), pwd.get()])
    messagebox.showinfo("Success", "Registered!")

def login():
    if not os.path.exists(USER_FILE):
        messagebox.showerror("Error", "No users found. Register first!")
        return

    with open(USER_FILE, "r") as f:
        for row in csv.reader(f):
            if len(row) < 3:
                continue
            if row[1] == user.get() and row[2] == pwd.get():
                open_dashboard(row[0])
                return

    messagebox.showerror("Error", "Invalid Login!")

# ---------------- DATE PICKER ---------------- #

def pick_date(entry):
    top = tk.Toplevel()
    cal = Calendar(top, date_pattern="yyyy-mm-dd")
    cal.pack()

    def select():
        entry.delete(0, tk.END)
        entry.insert(0, cal.get_date())
        top.destroy()

    tk.Button(top, text="Select", command=select).pack()

# ---------------- PRESCRIPTION ---------------- #

def generate_prescription():
    prescription.delete("1.0", tk.END)

    selected = table.selection()
    if selected:
        row_data = table.item(selected[0])['values']
        p_name = row_data[0]
        ref = row_data[1]
        addr = row_data[2]
        phone = row_data[3]
        issue = row_data[4]
        expiry = row_data[5]
        complaint = row_data[6]
        p_id = row_data[7]
        gender = row_data[8]
    else:
        try:
            p_name = entries["Patient Name"].get()
            ref = entries["Reference No"].get()
            addr = entries["Address"].get()
            phone = entries["Phone No"].get()
            issue = entries["Issue Date"].get()
            expiry = entries["Exp Date"].get()
            complaint = entries["Complaint"].get()
            p_id = entries["Patient ID"].get()
            gender = entries["Gender"].get()
            
            if not all([p_name, ref, addr, phone, issue, expiry, complaint, p_id, gender]):
                messagebox.showerror("Error", "Fill all fields or select a row!")
                return
        except KeyError:
            messagebox.showerror("Error", "Could not get data from fields!")
            return

    text = f"""
=========== HOSPITAL PRESCRIPTION ===========

Patient Name : {p_name}
Patient ID   : {p_id}
Gender       : {gender}

Reference No : {ref}
Complaint    : {complaint}

Address      : {addr}
Phone No     : {phone}

Issue Date   : {issue}
Expiry Date  : {expiry}

---------------------------------------------
Doctor Signature: ____________
"""
    prescription.insert(tk.END, text)

# ---------------- DASHBOARD ---------------- #

def open_dashboard(role):
    root.withdraw()

    dash = tk.Toplevel()
    dash.geometry("1200x700")
    dash.title("Hospital Management System")

    tk.Label(dash, text="HOSPITAL MANAGEMENT SYSTEM",
             font=("Arial", 25, "bold"),
             fg="red").pack(fill="x")

    # MENU
    menu_bar = tk.Menu(dash)
    menu_bar.add_command(label="Add", command=add_record)
    menu_bar.add_command(label="View", command=load_table)
    menu_bar.add_command(label="Update", command=update_record)
    menu_bar.add_command(label="Delete", command=delete_record)
    menu_bar.add_command(label="Clear", command=clear)
    menu_bar.add_command(label="Exit", command=lambda: logout(dash))
    dash.config(menu=menu_bar)

    main = tk.Frame(dash)
    main.pack(fill="both", expand=True)

    # FORM
    left = tk.LabelFrame(main, text="Patient Info")
    left.place(x=10, y=10, width=700, height=350)

    fields = [
        "Patient Name","Reference No","Address","Phone No",
        "Issue Date","Exp Date","Complaint",
        "Patient ID","Gender"
    ]

    global entries
    entries = {}

    for i, field in enumerate(fields):
        tk.Label(left, text=field).grid(row=i, column=0, padx=5, pady=5)
        e = tk.Entry(left)
        e.grid(row=i, column=1)
        entries[field] = e

        if "Date" in field:
            tk.Button(left, text="📅",
                      command=lambda ent=e: pick_date(ent)).grid(row=i, column=2)

    # PRESCRIPTION BOX
    right = tk.LabelFrame(main, text="Prescription")
    right.place(x=720, y=10, width=450, height=350)

    global prescription
    prescription = tk.Text(right)
    prescription.pack(fill="both", expand=True)

    # BUTTONS
    btn = tk.Frame(main)
    btn.place(x=15, y=320)

    tk.Button(btn, text="Add", command=add_record).grid(row=0, column=0)
    tk.Button(btn, text="Update", command=update_record).grid(row=0, column=1)
    tk.Button(btn, text="Delete", command=delete_record).grid(row=0, column=2)
    tk.Button(btn, text="Clear", command=clear).grid(row=0, column=3)
    tk.Button(btn, text="Generate", command=generate_prescription).grid(row=0, column=4)

    # TABLE
    table_frame = tk.Frame(main)
    table_frame.place(x=10, y=380, width=1150, height=250)

    global table
    columns = ("Patient Name", "Ref No", "Address", "Phone No", "Issue Date", "Exp Date", "Complaint", "Patient ID", "Gender")

    table = ttk.Treeview(table_frame, columns=columns, show="headings")

    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=120)

    table.pack(fill="both", expand=True)

    load_table()

# ---------------- FUNCTIONS ---------------- #

def add_record():
    data = [
        entries["Patient Name"].get(),
        entries["Reference No"].get(),
        entries["Address"].get(),
        entries["Phone No"].get(),
        entries["Issue Date"].get(),
        entries["Exp Date"].get(),
        entries["Complaint"].get(),
        entries["Patient ID"].get(),
        entries["Gender"].get()
    ]

    if "" in data:
        messagebox.showerror("Error", "Fill all fields!")
        return

    with open(FILE, "a", newline="") as f:
        csv.writer(f).writerow(data)

    load_table()

def load_table():
    table.delete(*table.get_children())

    if not os.path.exists(FILE):
        return

    with open(FILE, "r") as f:
        for row in csv.reader(f):
            table.insert("", tk.END, values=row)

def delete_record():
    selected = table.selection()
    if not selected:
        return

    idx = table.index(selected[0])

    data = []
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            data = list(csv.reader(f))

    if idx < len(data):
        del data[idx]

    with open(FILE, "w", newline="") as f:
        csv.writer(f).writerows(data)

    load_table()

def update_record():
    selected = table.selection()
    if not selected:
        return

    idx = table.index(selected[0])

    new_data = [
        entries["Patient Name"].get(),
        entries["Reference No"].get(),
        entries["Address"].get(),
        entries["Phone No"].get(),
        entries["Issue Date"].get(),
        entries["Exp Date"].get(),
        entries["Complaint"].get(),
        entries["Patient ID"].get(),
        entries["Gender"].get()
    ]

    data = []
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            data = list(csv.reader(f))

    if idx < len(data):
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

# ---------------- LOGIN UI ---------------- #

root = tk.Tk()
root.geometry("600x500")
root.title("Login")

frame = tk.Frame(root)
frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(frame, text="Hospital Login", font=("Arial", 16, "bold")).pack(pady=10)

role_var = tk.StringVar(value="Patient")
tk.OptionMenu(frame, role_var, "Patient", "Staff").pack()

input_frame = tk.Frame(frame)
input_frame.pack(pady=10)

tk.Label(input_frame, text="User Id:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
user = tk.Entry(input_frame)
user.grid(row=0, column=1, pady=5)

tk.Label(input_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
pwd = tk.Entry(input_frame, show="*")
pwd.grid(row=1, column=1, pady=5)

tk.Button(frame, text="Login", command=login).pack(pady=10)
tk.Button(frame, text="Register", command=register).pack()

root.mainloop()

import tkinter as tk
from tkinter import messagebox, ttk
import csv, os
from tkcalendar import Calendar

FILE = "hospital_data.csv"
USER_FILE = "users.csv"

# ---------------- LOGIN ---------------- #

def register():
    with open(USER_FILE, "a", newline="") as f:
        csv.writer(f).writerow([role_var.get(), user.get(), pwd.get()])
    messagebox.showinfo("Success", "Registered!")

def login():
    if not os.path.exists(USER_FILE):
        messagebox.showerror("Error", "No users found. Register first!")
        return

    with open(USER_FILE, "r") as f:
        for row in csv.reader(f):
            if len(row) < 3:
                continue
            if row[1] == user.get() and row[2] == pwd.get():
                open_dashboard(row[0])
                return

    messagebox.showerror("Error", "Invalid Login!")

# ---------------- DATE PICKER ---------------- #

def pick_date(entry):
    top = tk.Toplevel()
    cal = Calendar(top, date_pattern="yyyy-mm-dd")
    cal.pack()

    def select():
        entry.delete(0, tk.END)
        entry.insert(0, cal.get_date())
        top.destroy()

    tk.Button(top, text="Select", command=select).pack()

# ---------------- PRESCRIPTION ---------------- #

def generate_prescription():
    prescription.delete("1.0", tk.END)

    selected = table.selection()
    if selected:
        row_data = table.item(selected[0])['values']
        p_name = row_data[0]
        ref = row_data[1]
        addr = row_data[2]
        phone = row_data[3]
        issue = row_data[4]
        expiry = row_data[5]
        complaint = row_data[6]
        p_id = row_data[7]
        gender = row_data[8]
    else:
        try:
            p_name = entries["Patient Name"].get()
            ref = entries["Reference No"].get()
            addr = entries["Address"].get()
            phone = entries["Phone No"].get()
            issue = entries["Issue Date"].get()
            expiry = entries["Exp Date"].get()
            complaint = entries["Complaint"].get()
            p_id = entries["Patient ID"].get()
            gender = entries["Gender"].get()
            
            if not all([p_name, ref, addr, phone, issue, expiry, complaint, p_id, gender]):
                messagebox.showerror("Error", "Fill all fields or select a row!")
                return
        except KeyError:
            messagebox.showerror("Error", "Could not get data from fields!")
            return

    text = f"""
=========== HOSPITAL PRESCRIPTION ===========

Patient Name : {p_name}
Patient ID   : {p_id}
Gender       : {gender}

Reference No : {ref}
Complaint    : {complaint}

Address      : {addr}
Phone No     : {phone}

Issue Date   : {issue}
Expiry Date  : {expiry}

---------------------------------------------
Doctor Signature: ____________
"""
    prescription.insert(tk.END, text)

# ---------------- DASHBOARD ---------------- #

def open_dashboard(role):
    root.withdraw()

    dash = tk.Toplevel()
    dash.geometry("1200x700")
    dash.title("Hospital Management System")

    tk.Label(dash, text="HOSPITAL MANAGEMENT SYSTEM",
             font=("Arial", 25, "bold"),
             fg="red").pack(fill="x")

    # MENU
    menu_bar = tk.Menu(dash)
    menu_bar.add_command(label="Add", command=add_record)
    menu_bar.add_command(label="View", command=load_table)
    menu_bar.add_command(label="Update", command=update_record)
    menu_bar.add_command(label="Delete", command=delete_record)
    menu_bar.add_command(label="Clear", command=clear)
    menu_bar.add_command(label="Exit", command=lambda: logout(dash))
    dash.config(menu=menu_bar)

    main = tk.Frame(dash)
    main.pack(fill="both", expand=True)

    # FORM
    left = tk.LabelFrame(main, text="Patient Info")
    left.place(x=10, y=10, width=700, height=350)

    fields = [
        "Patient Name","Reference No","Address","Phone No",
        "Issue Date","Exp Date","Complaint",
        "Patient ID","Gender"
    ]

    global entries
    entries = {}

    for i, field in enumerate(fields):
        tk.Label(left, text=field).grid(row=i, column=0, padx=5, pady=5)
        e = tk.Entry(left)
        e.grid(row=i, column=1)
        entries[field] = e

        if "Date" in field:
            tk.Button(left, text="📅",
                      command=lambda ent=e: pick_date(ent)).grid(row=i, column=2)

    # PRESCRIPTION BOX
    right = tk.LabelFrame(main, text="Prescription")
    right.place(x=720, y=10, width=450, height=350)

    global prescription
    prescription = tk.Text(right)
    prescription.pack(fill="both", expand=True)

    # BUTTONS
    btn = tk.Frame(main)
    btn.place(x=15, y=320)

    tk.Button(btn, text="Add", command=add_record).grid(row=0, column=0)
    tk.Button(btn, text="Update", command=update_record).grid(row=0, column=1)
    tk.Button(btn, text="Delete", command=delete_record).grid(row=0, column=2)
    tk.Button(btn, text="Clear", command=clear).grid(row=0, column=3)
    tk.Button(btn, text="Generate", command=generate_prescription).grid(row=0, column=4)

    # TABLE
    table_frame = tk.Frame(main)
    table_frame.place(x=10, y=380, width=1150, height=250)

    global table
    columns = ("Patient Name", "Ref No", "Address", "Phone No", "Issue Date", "Exp Date", "Complaint", "Patient ID", "Gender")

    table = ttk.Treeview(table_frame, columns=columns, show="headings")

    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=120)

    table.pack(fill="both", expand=True)

    load_table()

# ---------------- FUNCTIONS ---------------- #

def add_record():
    data = [
        entries["Patient Name"].get(),
        entries["Reference No"].get(),
        entries["Address"].get(),
        entries["Phone No"].get(),
        entries["Issue Date"].get(),
        entries["Exp Date"].get(),
        entries["Complaint"].get(),
        entries["Patient ID"].get(),
        entries["Gender"].get()
    ]

    if "" in data:
        messagebox.showerror("Error", "Fill all fields!")
        return

    with open(FILE, "a", newline="") as f:
        csv.writer(f).writerow(data)

    load_table()

def load_table():
    table.delete(*table.get_children())

    if not os.path.exists(FILE):
        return

    with open(FILE, "r") as f:
        for row in csv.reader(f):
            table.insert("", tk.END, values=row)

def delete_record():
    selected = table.selection()
    if not selected:
        return

    idx = table.index(selected[0])

    data = []
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            data = list(csv.reader(f))

    if idx < len(data):
        del data[idx]

    with open(FILE, "w", newline="") as f:
        csv.writer(f).writerows(data)

    load_table()

def update_record():
    selected = table.selection()
    if not selected:
        return

    idx = table.index(selected[0])

    new_data = [
        entries["Patient Name"].get(),
        entries["Reference No"].get(),
        entries["Address"].get(),
        entries["Phone No"].get(),
        entries["Issue Date"].get(),
        entries["Exp Date"].get(),
        entries["Complaint"].get(),
        entries["Patient ID"].get(),
        entries["Gender"].get()
    ]

    data = []
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            data = list(csv.reader(f))

    if idx < len(data):
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

# ---------------- LOGIN UI ---------------- #

root = tk.Tk()
root.geometry("600x500")
root.title("Login")

frame = tk.Frame(root)
frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(frame, text="Hospital Login", font=("Arial", 16, "bold")).pack(pady=10)

role_var = tk.StringVar(value="Patient")
tk.OptionMenu(frame, role_var, "Patient", "Staff").pack()

input_frame = tk.Frame(frame)
input_frame.pack(pady=10)

tk.Label(input_frame, text="User Id:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
user = tk.Entry(input_frame)
user.grid(row=0, column=1, pady=5)

tk.Label(input_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
pwd = tk.Entry(input_frame, show="*")
pwd.grid(row=1, column=1, pady=5)

tk.Button(frame, text="Login", command=login).pack(pady=10)
tk.Button(frame, text="Register", command=register).pack()

root.mainloop()