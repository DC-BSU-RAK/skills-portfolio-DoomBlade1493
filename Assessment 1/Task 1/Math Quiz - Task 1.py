import tkinter as tk
from tkinter import messagebox
import random
import time
import pygame

class BreachMath:
    def __init__(self, root):
        self.root = root
        self.root.title("Cyberpunk: Math Protocol")
        self.root.geometry("980x700")
        self.root.minsize(900, 650)
        self.root.config(bg="#071017")

        pygame.mixer.init()
        pygame.mixer.music.load("BGM.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.3)
        self.fail_sfx = pygame.mixer.Sound("Fail.mp3")
        self.fail_sfx.set_volume(0.5)

        self.score = 0
        self.current_question = 0
        self.attempts = 0
        self.time_left = 0
        self.timer_running = False

        self.total_questions = 10
        self.difficulty = tk.StringVar(value="Easy")
        self.answer_var = tk.StringVar()
        self.question_text = tk.StringVar()
        self.node_text = tk.StringVar(value="> STANDBY")

        self.color_map = {"Easy": "#00ffd5", "Moderate": "#ffd84d", "Advanced": "#ff5d9e"}
        self.bg_primary = "#071017"
        self.neon_primary = "#00ffd5"
        self.neon_secondary = "#ffd84d"
        self.warn_color = "#ff5d9e"

        self.menu_frame = tk.Frame(self.root, bg=self.bg_primary)
        self.game_frame = tk.Frame(self.root, bg=self.bg_primary)

        self.create_menu()
        self.create_game_ui()

        self.anim_running = True
        self._bg_lines = [" " * 48 for _ in range(12)]
        self._bg_colors = [self.neon_primary for _ in range(12)]
        self._bg_tick()
        self.menu_frame.pack(fill="both", expand=True)

    def create_menu(self):
        header = tk.Label(self.menu_frame, text="MATH PROTOCOL", font=("Orbitron", 36, "bold"),
                          fg=self.neon_primary, bg=self.bg_primary)
        header.pack(pady=(40,10))
        sub = tk.Label(self.menu_frame, text="Calibrate your neural link. Solve the sequence.",
                       font=("Consolas", 14), fg=self.neon_secondary, bg=self.bg_primary)
        sub.pack(pady=(0,30))

        big_frame = tk.Frame(self.menu_frame, bg=self.bg_primary)
        big_frame.pack(pady=10)

        def make_btn(text, color, cmd):
            b = tk.Button(big_frame, text=text, font=("OCR A Extended", 13, "bold"),
                          width=36, height=2, bg=color, fg="#071017", bd=0,
                          activebackground="#ffffff", activeforeground="#000", command=cmd)
            b.bind("<Enter>", lambda e, w=b: w.config(bg="#ffffff", fg=color))
            b.bind("<Leave>", lambda e, w=b, c=color: w.config(bg=c, fg="#071017"))
            return b

        b_easy = make_btn("BREACH: LOW SECURITY", self.color_map["Easy"], lambda: self.start("Easy"))
        b_med = make_btn("BREACH: MEDIUM SECURITY", self.color_map["Moderate"], lambda: self.start("Moderate"))
        b_hard = make_btn("BREACH: HIGH SECURITY", self.color_map["Advanced"], lambda: self.start("Advanced"))

        b_easy.pack(pady=12)
        b_med.pack(pady=12)
        b_hard.pack(pady=12)

        footer = tk.Label(self.menu_frame, text="System boot sequence online...", font=("Consolas", 11, "italic"),
                          fg="#8aa0a9", bg=self.bg_primary)
        footer.pack(side="bottom", pady=30)

    def create_game_ui(self):
        top = tk.Frame(self.game_frame, bg=self.bg_primary)
        top.pack(fill="x", pady=(18,6))

        self.title_label = tk.Label(top, text="BREACH INTERFACE", font=("Orbitron", 20, "bold"),
                                    fg=self.neon_primary, bg=self.bg_primary)
        self.title_label.pack(side="left", padx=20)

        self.difficulty_label = tk.Label(top, text="Security: Easy", font=("Consolas", 13, "bold"),
                                         fg=self.neon_secondary, bg=self.bg_primary)
        self.difficulty_label.pack(side="left", padx=12)

        self.score_label = tk.Label(top, text="Trace Data: 0", font=("Consolas", 13),
                                    fg="#bfeee6", bg=self.bg_primary)
        self.score_label.pack(side="right", padx=20)

        mid = tk.Frame(self.game_frame, bg=self.bg_primary)
        mid.pack(fill="both", expand=True, padx=24, pady=6)

        left_panel = tk.Frame(mid, bg=self.bg_primary)
        left_panel.pack(side="left", fill="y", padx=(0,12))

        self.node_box = tk.Label(left_panel, textvariable=self.node_text, font=("Consolas", 11),
                                 fg=self.neon_primary, bg="#041018", width=22, height=20, anchor="nw",
                                 justify="left", bd=1, relief="solid")
        self.node_box.pack()

        center_panel = tk.Frame(mid, bg=self.bg_primary)
        center_panel.pack(side="left", expand=True, fill="both")

        node_frame = tk.Frame(center_panel, bg="#041018", bd=2, relief="ridge")
        node_frame.pack(pady=20, ipadx=10, ipady=20, expand=True)

        self.question_label = tk.Label(node_frame, textvariable=self.question_text,
                                       font=("Orbitron", 28, "bold"), fg="#ffffff", bg="#041018")
        self.question_label.pack(pady=(20,10))

        self.progress_label = tk.Label(node_frame, text="Sequence: 1 / 10", font=("Consolas", 12),
                                       fg=self.neon_primary, bg="#041018")
        self.progress_label.pack()

        self.timer_bar_bg = tk.Frame(node_frame, bg="#092027", height=12)
        self.timer_bar_bg.pack(fill="x", padx=30, pady=(12,18))
        self.timer_fill = tk.Frame(self.timer_bar_bg, bg=self.neon_secondary, width=0, height=12)
        self.timer_fill.place(x=0, y=0)

        entry_frame = tk.Frame(node_frame, bg="#041018")
        entry_frame.pack(pady=8)

        v = tk.Entry(entry_frame, textvariable=self.answer_var, font=("Consolas", 16),
                     width=12, justify="center", bg="#071017", fg=self.neon_primary,
                     insertbackground=self.neon_primary, bd=0)
        v.pack(pady=6)
        v.bind("<Return>", lambda e: self.check())

        btn_frame = tk.Frame(node_frame, bg="#041018")
        btn_frame.pack(pady=12)

        self.exec_btn = tk.Button(btn_frame, text="DEPLOY ANSWER", font=("OCR A Extended", 12, "bold"),
                                  bg="#00a7d1", fg="#071017", width=18, height=1, bd=0, command=self.check)
        self.exec_btn.grid(row=0, column=0, padx=8)

        self.abort_btn = tk.Button(btn_frame, text="TERMINATE SESSION", font=("OCR A Extended", 12, "bold"),
                                   bg="#ff4e8a", fg="#071017", width=18, height=1, bd=0, command=self.abort_to_menu)
        self.abort_btn.grid(row=0, column=1, padx=8)

        right_panel = tk.Frame(mid, bg=self.bg_primary)
        right_panel.pack(side="left", fill="y", padx=(12,0))
        hint_box = tk.Label(right_panel, text="NODE MATRIX", font=("Consolas", 12, "bold"),
                            fg="#bfeee6", bg="#041018", width=28, height=8, bd=1, relief="solid")
        hint_box.pack(pady=(0,12))
        self.feedback = tk.Label(right_panel, text="Status: Idle", font=("Consolas", 12),
                                 fg="#a6f7ea", bg="#041018", width=28, height=8, bd=1, relief="solid",
                                 anchor="nw", justify="left")
        self.feedback.pack()

    def start(self, level):
        self.difficulty.set(level)
        self.score = 0
        self.current_question = 0
        self.attempts = 0
        self.timer_running = False
        self.node_text.set("> INITIALIZING SEQUENCE\n> SYNCING...")
        self.menu_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)
        col = self.color_for(level)
        self.title_label.config(fg=col)
        self.difficulty_label.config(text=f"Security: {level}", fg=col)
        self.score_label.config(text="Trace Data: 0")
        self.progress_label.config(text=f"Sequence: 1 / {self.total_questions}", fg=self.neon_primary)
        self.root.after(260, self.boot_sequence)
        pygame.mixer.music.fadeout(1000)
        time.sleep(1)
        pygame.mixer.music.load("IGM.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.4)

    def boot_sequence(self):
        self.node_text.set("> NEURAL LINK STABLE\n> LAUNCHING NODE GRID")
        self.root.after(380, self.next_question)

    def color_for(self, level):
        return self.color_map.get(level, self.neon_primary)

    def random_int(self, difficulty):
        if difficulty == "Easy":
            return random.randint(0, 9)
        if difficulty == "Moderate":
            return random.randint(10, 99)
        return random.randint(100, 999)

    def decide_operation(self):
        return random.choice(["+", "-", "*", "/"])

    def next_question(self):
        if self.current_question >= self.total_questions:
            self.show_results()
            return
        level = self.difficulty.get()
        a = self.random_int(level)
        b = self.random_int(level)
        op = self.decide_operation()
        if op == "/":
            b = random.randint(1, 9)
            a = b * random.randint(1, 9)
        if op == "+":
            self.correct = a + b
        elif op == "-":
            self.correct = a - b
        elif op == "*":
            self.correct = a * b
        else:
            self.correct = a // b
        self.question_text.set(f"{a}  {op}  {b}  =  ?")
        self.answer_var.set("")
        self.attempts = 0
        prog_color = self.neon_primary
        if self.current_question >= int(self.total_questions * 0.7):
            prog_color = self.warn_color
        elif self.current_question >= int(self.total_questions * 0.4):
            prog_color = self.neon_secondary
        self.progress_label.config(text=f"Sequence: {self.current_question + 1} / {self.total_questions}", fg=prog_color)
        self.node_text.set(self.generate_node_display())
        self.score_label.config(text=f"Trace Data: {self.score}")
        self.set_timer_for_level(level)
        self.start_timer_bar()

    def set_timer_for_level(self, level):
        if level == "Easy":
            self.time_left = 10
            self.timer_running = False
            self.timer_fill.place_configure(width=0)
        elif level == "Moderate":
            self.time_left = 12
            self.timer_running = True
        else:
            self.time_left = 16
            self.timer_running = True

    def start_timer_bar(self):
        self.timer_total = max(self.time_left, 1)
        self.timer_start_time = time.time()
        if self.timer_running:
            self.update_timer_bar()
        else:
            self.timer_fill.place_configure(width=0)

    def update_timer_bar(self):
        if not self.timer_running:
            return
        elapsed = time.time() - self.timer_start_time
        remaining = self.time_left - elapsed
        if remaining < 0:
            remaining = 0
        total = self.timer_total
        frac = remaining / total if total else 0
        full_width = self.timer_bar_bg.winfo_width() or (self.root.winfo_width() // 2)
        fill_w = int(full_width * frac)
        color = self.neon_secondary if frac > 0.4 else self.warn_color
        self.timer_fill.config(bg=color)
        self.timer_fill.place_configure(width=fill_w)
        if remaining <= 0:
            self.timer_running = False
            self.timer_expired()
            return
        self.root.after(120, self.update_timer_bar)

    def timer_expired(self):
        self.flash_node(self.warn_color)
        self.feedback.config(text=f"Status: Timer expired. Node failed.", fg=self.warn_color)
        self.fail_sfx.play()
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.root.after(550, self.next_question)
        else:
            self.root.after(350, self.show_results)

    def check(self):
        if self.timer_running:
            self.timer_running = False
        val = self.answer_var.get().strip()
        try:
            ans = int(val)
        except:
            messagebox.showwarning("Input Error", "Invalid input detected. Please enter an integer.")
            return
        if ans == self.correct:
            self.score += 10 if self.attempts == 0 else 5
            self.feedback.config(text="Status: Node cracked. Data captured.", fg=self.neon_primary)
            self.flash_node(self.neon_primary)
        else:
            self.attempts += 1
            self.feedback.config(text=f"Status: Incorrect code. Attempts: {self.attempts}", fg=self.warn_color)
            self.flash_node(self.warn_color)
            self.fail_sfx.play()
            if self.attempts < 2:
                self.timer_running = True
                self.timer_start_time = time.time()
                self.update_timer_bar()
                return
        self.current_question += 1
        if self.current_question < self.total_questions:
            self.root.after(350, self.next_question)
        else:
            self.root.after(250, self.show_results)

    def abort_to_menu(self):
        if messagebox.askyesno("Abort", "Terminate session and return to menu?"):
            self.timer_running = False
            pygame.mixer.music.fadeout(500)
            time.sleep(0.5)
            pygame.mixer.music.load("BGM.mp3")
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.3)
            self.game_frame.pack_forget()
            self.menu_frame.pack(fill="both", expand=True)

    def flash_node(self, color):
        orig_q = self.question_label.cget("fg")
        orig_p = self.progress_label.cget("fg")
        self.question_label.config(fg=color)
        self.progress_label.config(fg=color)
        self.root.update()
        self.root.after(110, lambda: (self.question_label.config(fg=orig_q), self.progress_label.config(fg=orig_p)))

    def show_results(self):
        self.timer_running = False
        rank = "F"
        if self.score >= 100:
            rank = "S"
        elif self.score >= 90:
            rank = "A+"
        elif self.score >= 80:
            rank = "A"
        elif self.score >= 70:
            rank = "B"
        elif self.score >= 60:
            rank = "C"
        elif self.score >= 50:
            rank = "D"
        pygame.mixer.music.fadeout(500)
        time.sleep(0.5)
        pygame.mixer.music.load("BGM.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.3)

        messagebox.showinfo(
            "Simulation Complete",
            f"Data Upload Successful.\nFinal Score: {self.score}/{self.total_questions * 10}\n"
            f"Performance Rank: {rank}\n\nSession terminated."
        )
        self.game_frame.pack_forget()
        self.menu_frame.pack(fill="both", expand=True)

    def generate_node_display(self):
        lines = []
        lines.append("> NODE GRID ONLINE")
        lines.append("> TRACE ID: " + format(random.randint(0, 0xFFFF), '04X'))
        for i in range(12):
            chunk = ''.join(random.choice("0123456789ABCDEF") for _ in range(16))
            lines.append("  " + chunk)
        return "\n".join(lines)

    def _bg_tick(self):
        if not self.anim_running:
            return
        new_line = ''.join(random.choice("0123456789ABCDEF") for _ in range(48))
        self._bg_lines.pop(0)
        self._bg_lines.append(new_line)
        for i in range(len(self._bg_colors)):
            if random.random() < 0.2:
                self._bg_colors[i] = random.choice([self.neon_primary, self.neon_secondary, "#ffffff"])
        display_text = "\n".join(self._bg_lines)
        self.node_box.config(text=display_text, fg=random.choice([self.neon_primary, self.neon_secondary, "#ffffff"]))
        self.root.after(200, self._bg_tick)

if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap("cyberlogo.ico")
    app = BreachMath(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (pygame.mixer.music.stop(), root.destroy()))
    root.mainloop()