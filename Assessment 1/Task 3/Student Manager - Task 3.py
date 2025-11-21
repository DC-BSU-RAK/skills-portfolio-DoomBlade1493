import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import csv
import os
import random

FILE_NAME = "studentMarks.txt"
BG = "#0b0b0b"
PANEL = "#111111"
ACCENT = "#C62828"
ACCENT2 = "#B71C1C"
TEXT = "#FFFFFF"
MUTED = "#A0A0A0"
CARD = "#0f1720"
ALTERNATE = "#0e1315"
GRADE_COLORS = {"A": "#4CAF50", "B": "#4CAF50", "C": "#FFC107", "D": "#FFC107", "F": "#F44336"}
ARROWS = ["↑", "↓", "←", "→"]

def load_students():
    students = []
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, "w") as f:
            f.write("0\n")
        return students
    with open(FILE_NAME, "r") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    if not lines:
        return students
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) < 6:
            continue
        code = parts[0].strip()
        name = parts[1].strip()
        try:
            cw1 = int(parts[2]); cw2 = int(parts[3]); cw3 = int(parts[4]); exam = int(parts[5])
        except:
            continue
        total = cw1 + cw2 + cw3
        overall = (total + exam) / 160 * 100
        grade = compute_grade(overall)
        students.append({"code": code, "name": name, "cw1": cw1, "cw2": cw2, "cw3": cw3, "exam": exam, "total": total, "overall": overall, "grade": grade})
    return students

def save_students(students):
    with open(FILE_NAME, "w") as f:
        f.write(f"{len(students)}\n")
        for s in students:
            f.write(f"{s['code']},{s['name']},{s['cw1']},{s['cw2']},{s['cw3']},{s['exam']}\n")

def compute_grade(p):
    if p >= 70: return "A"
    if p >= 60: return "B"
    if p >= 50: return "C"
    if p >= 40: return "D"
    return "F"

def summary_stats(students):
    if not students:
        return 0.0, None, None
    avg = sum(s["overall"] for s in students) / len(students)
    top = max(students, key=lambda x: x["overall"])
    bot = min(students, key=lambda x: x["overall"])
    return avg, top, bot

class ArrowMiniGame(tk.Toplevel):
    def __init__(self, parent, length=6, speed=700):
        super().__init__(parent)
        self.title("Access Challenge")
        self.configure(bg="#111111")
        self.geometry("400x250")
        self.sequence_length = length
        self.speed = speed
        self.sequence = [random.choice(ARROWS) for _ in range(self.sequence_length)]
        self.index = 0
        self.result = False
        self.displayed_index = 0

        tk.Label(self, text="Repeat the arrow sequence!", fg="#FFC107", bg="#111111", 
                 font=("Segoe UI", 14, "bold")).pack(pady=12)

        self.seq_label = tk.Label(self, text="", fg="#FFFFFF", bg="#111111", font=("Segoe UI", 24, "bold"))
        self.seq_label.pack(pady=10)

        self.user_label = tk.Label(self, text="", fg="#4CAF50", bg="#111111", font=("Segoe UI", 20, "bold"))
        self.user_label.pack(pady=10)

        self.after(500, self.show_next_arrow)

        self.bind_all("<Key>", self.key_press)
        self.focus_force()
        self.grab_set()
        self.wait_window(self)

    def show_next_arrow(self):
        if self.displayed_index < len(self.sequence):
            display_text = " ".join(self.sequence[:self.displayed_index+1])
            self.seq_label.config(text=display_text)
            self.displayed_index += 1
            self.after(self.speed, self.show_next_arrow)
        else:
            self.seq_label.config(text="Now repeat it!")

    def key_press(self, event):
        key_map = {"Up": "↑", "Down": "↓", "Left": "←", "Right": "→"}
        if event.keysym not in key_map:
            return

        current_arrow = key_map[event.keysym]
        self.user_label.config(text=self.user_label.cget("text") + current_arrow)

        if current_arrow != self.sequence[self.index]:
            tk.messagebox.showerror("Failed", f"Wrong arrow! Expected {self.sequence[self.index]}")
            self.destroy()
            return

        self.index += 1
        if self.index == len(self.sequence):
            tk.messagebox.showinfo("Success", "Access granted!")
            self.result = True
            self.destroy()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.iconbitmap("Icon.ico")
        self.title("Ultravista Academy • Student Manager")
        self.geometry("1100x680")
        self.configure(bg=BG)
        self.students = []
        self.filtered = []
        self.sort_state = None
        self.hover = None
        self.setup_style()
        self.build_ui()
        self.bind_shortcuts()
        self.load_refresh()

    def setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT, rowheight=30, font=("Segoe UI", 11))
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), foreground=ACCENT, background=BG)
        style.map("Treeview", background=[("selected", ACCENT2)])
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        self.style = style

    def build_ui(self):
        top = tk.Frame(self, bg=BG, height=72)
        top.pack(side="top", fill="x")
        tk.Label(top, text="ULTRAVISTA ACADEMY", bg=BG, fg=ACCENT, font=("Segoe UI", 14, "bold")).place(x=18, y=12)
        tk.Label(top, text="Student Manager", bg=BG, fg=TEXT, font=("Segoe UI", 11)).place(x=20, y=36)
        btn_export = tk.Button(top, text="Export CSV", bg=ACCENT, fg=TEXT, bd=0, activebackground=ACCENT2, command=self.export_csv)
        btn_export.place(x=970, y=20, width=100, height=34)
        btn_refresh = tk.Button(top, text="Refresh", bg="#2a2a2a", fg=TEXT, bd=0, command=self.load_refresh)
        btn_refresh.place(x=860, y=20, width=100, height=34)

        sidebar = tk.Frame(self, bg="#050505", width=220)
        sidebar.pack(side="left", fill="y")
        menu_items = [
            ("View All", self.action_view_all),
            ("View Individual", self.action_view_individual),
            ("Highest Overall", self.action_highest),
            ("Lowest Overall", self.action_lowest),
            ("Sort Records", self.action_sort),
            ("Add Student", self.action_add),
            ("Update Student", self.action_update),
            ("Delete Student", self.action_delete)
        ]
        y = 30
        for t, cmd in menu_items:
            b = tk.Button(sidebar, text=t, bg=BG, fg=TEXT, bd=0, activebackground=ACCENT2, command=cmd)
            b.place(x=14, y=y, width=192, height=42)
            y += 54

        main = tk.Frame(self, bg=BG)
        main.pack(side="left", fill="both", expand=True, padx=18, pady=12)

        cards = tk.Frame(main, bg=BG)
        cards.pack(fill="x")
        self.card_total = self.make_card(cards, "Total Students", "—")
        self.card_avg = self.make_card(cards, "Average %", "—")
        self.card_top = self.make_card(cards, "Top Student", "—")
        self.card_bot = self.make_card(cards, "Lowest Student", "—")

        search_f = tk.Frame(main, bg=BG)
        search_f.pack(fill="x", pady=(12,8))
        tk.Label(search_f, text="Search:", bg=BG, fg=TEXT, font=("Segoe UI", 10)).pack(side="left", padx=(4,6))
        self.search_var = tk.StringVar()
        search_e = tk.Entry(search_f, textvariable=self.search_var, bg="#0d0d0d", fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 11))
        search_e.pack(side="left", padx=(0,8))
        search_e.bind("<KeyRelease>", lambda e: self.apply_filter())
        tk.Button(search_f, text="Clear", bg="#1f1f1f", fg=TEXT, bd=0, command=self.clear_search).pack(side="left")

        table_wrap = tk.Frame(main, bg=BG)
        table_wrap.pack(fill="both", expand=True, pady=(6,0))
        cols = ("Code", "Name", "Total CW", "Exam", "Overall %", "Grade")
        self.tree = ttk.Treeview(table_wrap, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center", width=140)
        self.tree.pack(fill="both", expand=True, side="left")
        vs = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        vs.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vs.set)
        self.tree.bind("<Motion>", self.on_motion)
        self.tree.bind("<Leave>", lambda e: self.clear_hover())
        self.tree.bind("<Double-1>", lambda e: self.open_selected())
        footer = tk.Frame(main, bg=BG, height=6)
        footer.pack(fill="x")

    def bind_shortcuts(self):
        self.bind("<Control-n>", lambda e: self.action_add())
        self.bind("<Control-f>", lambda e: self.focus_search())

    def focus_search(self):
        self.focus_force()
        self.after(40, lambda: self.focus_get())

    def make_card(self, parent, title, value):
        f = tk.Frame(parent, bg=CARD, padx=16, pady=10)
        f.pack(side="left", padx=8)
        tk.Label(f, text=title, bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w")
        v = tk.Label(f, text=value, bg=CARD, fg=TEXT, font=("Segoe UI", 13, "bold"))
        v.pack(anchor="w", pady=(6,0))
        return v

    def load_refresh(self):
        self.students = load_students()
        self.filtered = list(self.students)
        self.refresh_table()
        self.refresh_cards()

    def refresh_table(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for i, s in enumerate(self.filtered):
            vals = (s["code"], s["name"], s["total"], s["exam"], f"{s['overall']:.2f}", s["grade"])
            iid = self.tree.insert("", "end", values=vals, tags=(s["grade"],))
            if i % 2 == 0:
                self.tree.tag_configure(iid, background=PANEL)
            else:
                self.tree.tag_configure(iid, background=ALTERNATE)
        for g, col in GRADE_COLORS.items():
            self.tree.tag_configure(g, foreground=col)

    def refresh_cards(self):
        avg, top, bot = summary_stats(self.students)
        self.card_total.config(text=str(len(self.students)))
        self.card_avg.config(text=f"{avg:.2f}" if self.students else "—")
        self.card_top.config(text=f"{top['name']} ({top['code']})" if top else "—")
        self.card_bot.config(text=f"{bot['name']} ({bot['code']})" if bot else "—")

    def apply_filter(self):
        q = self.search_var.get().strip().lower()
        if q == "":
            self.filtered = list(self.students)
        else:
            self.filtered = [s for s in self.students if q in s["name"].lower() or q in s["code"]]
        self.refresh_table()

    def clear_search(self):
        self.search_var.set("")
        self.apply_filter()

    def on_motion(self, event):
        row = self.tree.identify_row(event.y)
        if row != self.hover:
            self.clear_hover()
            if row:
                self.tree.item(row, tags=self.tree.item(row, "tags") + ("hover",))
                self.tree.tag_configure("hover", background="#1c2a2f")
                self.hover = row

    def clear_hover(self):
        if self.hover:
            tags = tuple(t for t in self.tree.item(self.hover, "tags") if t != "hover")
            self.tree.item(self.hover, tags=tags)
            self.hover = None

    def open_selected(self):
        sel = self.tree.focus()
        if not sel:
            return
        vals = self.tree.item(sel, "values")
        code = vals[0]
        student = next((s for s in self.students if s["code"] == code), None)
        if student:
            self.show_student_popup(student, "Student Record")

    def show_student_popup(self, s, title="Student"):
        text = f"Name: {s['name']}\nCode: {s['code']}\nCoursework total: {s['total']} / 60\nExam: {s['exam']} / 100\nOverall: {s['overall']:.2f} %\nGrade: {s['grade']}"
        messagebox.showinfo(title, text)

    def action_view_all(self):
        self.load_refresh()
        avg, _, _ = summary_stats(self.students)
        if self.students:
            messagebox.showinfo("Summary", f"Total students: {len(self.students)}\nAverage overall %: {avg:.2f}")
        else:
            messagebox.showinfo("Summary", "No students found")

    def action_view_individual(self):
        code = simpledialog.askstring("Select Student", "Enter student code:", parent=self)
        if not code:
            return
        student = next((s for s in self.students if s["code"] == code), None)
        if not student:
            messagebox.showinfo("Not found", f"No student with code {code}")
            return
        self.show_student_popup(student)

    def action_highest(self):
        if not self.students:
            messagebox.showinfo("Info", "No students")
            return
        top = max(self.students, key=lambda x: x["overall"])
        self.show_student_popup(top, "Highest Overall")

    def action_lowest(self):
        if not self.students:
            messagebox.showinfo("Info", "No students")
            return
        bot = min(self.students, key=lambda x: x["overall"])
        self.show_student_popup(bot, "Lowest Overall")

    def action_sort(self):
        order = simpledialog.askstring("Sort Order", "Enter 'asc' or 'desc':", parent=self)
        if not order:
            return
        order = order.strip().lower()
        if order not in ("asc", "desc"):
            messagebox.showerror("Error", "Invalid option")
            return
        reverse = (order == "desc")
        self.students.sort(key=lambda x: x["overall"], reverse=reverse)
        save_students(self.students)
        self.apply_filter()
        self.refresh_cards()
        messagebox.showinfo("Sorted", f"Records sorted {'descending' if reverse else 'ascending'} by overall %")

    def action_add(self):
        mini = ArrowMiniGame(self)
        if not getattr(mini, "result", False):
            return
        form = StudentForm(self, title="Add Student")
        self.wait_window(form)
        if form.result:
            s = form.result
            s["total"] = s["cw1"] + s["cw2"] + s["cw3"]
            s["overall"] = (s["total"] + s["exam"]) / 160 * 100
            s["grade"] = compute_grade(s["overall"])
            self.students.append(s)
            save_students(self.students)
            self.apply_filter()
            self.refresh_cards()

    def action_update(self):
        mini = ArrowMiniGame(self)
        if not getattr(mini, "result", False):
            return
        sel = self.tree.focus()
        if not sel:
            messagebox.showinfo("Select", "Select a row to update (double-click to open).")
            return
        vals = self.tree.item(sel, "values")
        code = vals[0]
        student = next((s for s in self.students if s["code"] == code), None)
        if not student:
            return
        form = StudentForm(self, title="Update Student", student=student)
        self.wait_window(form)
        if form.result:
            r = form.result
            student["name"] = r["name"]
            student["cw1"] = r["cw1"]; student["cw2"] = r["cw2"]; student["cw3"] = r["cw3"]; student["exam"] = r["exam"]
            student["total"] = student["cw1"] + student["cw2"] + student["cw3"]
            student["overall"] = (student["total"] + student["exam"]) / 160 * 100
            student["grade"] = compute_grade(student["overall"])
            save_students(self.students)
            self.apply_filter()
            self.refresh_cards()

    def action_delete(self):
        mini = ArrowMiniGame(self)
        if not getattr(mini, "result", False):
            return
        sel = self.tree.focus()
        if not sel:
            messagebox.showinfo("Select", "Select a row to delete")
            return
        vals = self.tree.item(sel, "values")
        code = vals[0]
        student = next((s for s in self.students if s["code"] == code), None)
        if not student:
            return
        if messagebox.askyesno("Confirm", f"Delete {student['name']} ({student['code']})?"):
            self.students = [x for x in self.students if x["code"] != code]
            save_students(self.students)
            self.apply_filter()
            self.refresh_cards()

    def export_csv(self):
        if not self.students:
            messagebox.showinfo("Export", "No students to export")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path:
            return
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Code","Name","CW1","CW2","CW3","Exam","TotalCW","Overall%","Grade"])
            for s in self.students:
                w.writerow([s["code"], s["name"], s["cw1"], s["cw2"], s["cw3"], s["exam"], s["total"], f"{s['overall']:.2f}", s["grade"]])
        messagebox.showinfo("Export", f"Exported {len(self.students)} records to {path}")

class StudentForm(tk.Toplevel):
    def __init__(self, parent, title="Student", student=None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=PANEL)
        self.geometry("420x380")
        self.result = None
        self.student = student
        self.build()
        if student:
            self.load(student)

    def build(self):
        tk.Label(self, text="Code (1000-9999):", bg=PANEL, fg=MUTED, font=("Segoe UI", 10)).place(x=22, y=22)
        self.code_e = tk.Entry(self, bg="#0c0c0c", fg=TEXT, insertbackground=TEXT, bd=0, relief="flat", font=("Segoe UI", 11))
        self.code_e.place(x=220, y=20, width=180)
        tk.Label(self, text="Name:", bg=PANEL, fg=MUTED, font=("Segoe UI", 10)).place(x=22, y=72)
        self.name_e = tk.Entry(self, bg="#0c0c0c", fg=TEXT, insertbackground=TEXT, bd=0, relief="flat", font=("Segoe UI", 11))
        self.name_e.place(x=220, y=70, width=180)
        tk.Label(self, text="CW1 (0-20):", bg=PANEL, fg=MUTED, font=("Segoe UI", 10)).place(x=22, y=122)
        self.cw1_e = tk.Entry(self, bg="#0c0c0c", fg=TEXT, insertbackground=TEXT, bd=0, relief="flat", font=("Segoe UI", 11))
        self.cw1_e.place(x=220, y=120, width=80)
        tk.Label(self, text="CW2 (0-20):", bg=PANEL, fg=MUTED, font=("Segoe UI", 10)).place(x=22, y=162)
        self.cw2_e = tk.Entry(self, bg="#0c0c0c", fg=TEXT, insertbackground=TEXT, bd=0, relief="flat", font=("Segoe UI", 11))
        self.cw2_e.place(x=220, y=160, width=80)
        tk.Label(self, text="CW3 (0-20):", bg=PANEL, fg=MUTED, font=("Segoe UI", 10)).place(x=22, y=202)
        self.cw3_e = tk.Entry(self, bg="#0c0c0c", fg=TEXT, insertbackground=TEXT, bd=0, relief="flat", font=("Segoe UI", 11))
        self.cw3_e.place(x=220, y=200, width=80)
        tk.Label(self, text="Exam (0-100):", bg=PANEL, fg=MUTED, font=("Segoe UI", 10)).place(x=22, y=242)
        self.exam_e = tk.Entry(self, bg="#0c0c0c", fg=TEXT, insertbackground=TEXT, bd=0, relief="flat", font=("Segoe UI", 11))
        self.exam_e.place(x=220, y=240, width=80)
        btn = tk.Button(self, text="Save", bg=ACCENT, fg=TEXT, bd=0, command=self.on_save)
        btn.place(x=160, y=300, width=100, height=36)

    def load(self, s):
        self.code_e.insert(0, s["code"])
        self.code_e.config(state="disabled")
        self.name_e.insert(0, s["name"])
        self.cw1_e.insert(0, str(s["cw1"]))
        self.cw2_e.insert(0, str(s["cw2"]))
        self.cw3_e.insert(0, str(s["cw3"]))
        self.exam_e.insert(0, str(s["exam"]))

    def on_save(self):
        code = self.code_e.get().strip()
        name = self.name_e.get().strip()
        try:
            cw1 = int(self.cw1_e.get())
            cw2 = int(self.cw2_e.get())
            cw3 = int(self.cw3_e.get())
            exam = int(self.exam_e.get())
        except:
            messagebox.showerror("Invalid", "Please enter numeric marks")
            return
        if not code.isdigit() or not (1000 <= int(code) <= 9999):
            messagebox.showerror("Invalid", "Code must be 1000-9999")
            return
        for v, lim in ((cw1,20),(cw2,20),(cw3,20)):
            if not (0 <= v <= lim):
                messagebox.showerror("Invalid", "Coursework marks must be 0-20")
                return
        if not (0 <= exam <= 100):
            messagebox.showerror("Invalid", "Exam must be 0-100")
            return
        self.result = {"code": code, "name": name, "cw1": cw1, "cw2": cw2, "cw3": cw3, "exam": exam}
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()