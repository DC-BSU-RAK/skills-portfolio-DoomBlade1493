import tkinter as tk
from PIL import Image, ImageTk
import random
import os
import pygame

class CodecJokes:
    def __init__(self, root):
        self.root = root
        self.root.title("Codec Jokes")
        self.root.iconbitmap("Icon.ico")
        self.root.geometry("800x400")
        self.root.config(bg="#001100")

        pygame.mixer.init()
        if os.path.exists("BGM.mp3"):
            pygame.mixer.music.load("BGM.mp3")
            pygame.mixer.music.set_volume(0.25)
            pygame.mixer.music.play(-1)

        self.joke_sfx = pygame.mixer.Sound("Codec.wav")
        self.laugh_sfx = pygame.mixer.Sound("Laugh.wav")
        self.joke_channel = pygame.mixer.Channel(1)
        self.laugh_channel = pygame.mixer.Channel(2)

        try:
            with open("randomJokes.txt", "r", encoding="utf-8") as f:
                self.jokes = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            tk.messagebox.showerror("File Missing", "randomJokes.txt not found!")
            self.root.destroy()
            return

        self.face_images = []
        for i in range(1, 9):
            path = os.path.join("Faces", f"{i}.jpg")
            if os.path.exists(path):
                img = Image.open(path).resize((182, 304))
                self.face_images.append(ImageTk.PhotoImage(img))
            else:
                tk.messagebox.showerror("File Missing", f"{path} not found!")
                self.root.destroy()
                return

        self.used_faces = []
        self.current_joke = None
        self.typing_job = None
        self.next_punchline = ""
        self.snake_face = self.face_images[0]

        left_width = 182
        right_width = 182
        padding = 40
        center_width = 800 - left_width - right_width - padding

        self.left_frame = tk.Frame(self.root, bg="#001100", width=left_width, height=380)
        self.left_frame.pack(side="left", padx=10, pady=10)
        self.left_frame.pack_propagate(False)
        self.caller_face_label = tk.Label(self.left_frame, bg="#001100")
        self.caller_face_label.pack(expand=True)

        self.right_frame = tk.Frame(self.root, bg="#001100", width=right_width, height=380)
        self.right_frame.pack(side="right", padx=10, pady=10)
        self.right_frame.pack_propagate(False)
        self.listener_face_label = tk.Label(self.right_frame, bg="#001100", image=self.snake_face)
        self.listener_face_label.pack(expand=True)
        self.listener_face_label.image = self.snake_face

        self.center_frame = tk.Frame(self.root, bg="#001100", width=center_width, height=380)
        self.center_frame.pack(side="left", padx=10, pady=10)
        self.center_frame.pack_propagate(False)

        self.dialogue_label = tk.Label(
            self.center_frame, text="", font=("Consolas", 11, "bold"),
            fg="#00FF00", bg="#001100", wraplength=center_width, justify="left", anchor="nw"
        )
        self.dialogue_label.pack(fill="both", expand=True, padx=10, pady=10)

        self.button_frame = tk.Frame(self.center_frame, bg="#001100")
        self.button_frame.pack(pady=5, anchor="nw")
        self.joke_btn = tk.Button(
            self.button_frame, text="ALEXA TELL ME A JOKE", command=self.show_joke,
            bg="#003300", fg="#00FF00", font=("Consolas", 10, "bold"), width=25
        )
        self.joke_btn.grid(row=0, column=0, padx=5, pady=2)
        self.punch_btn = tk.Button(
            self.button_frame, text="SHOW PUNCHLINE", command=self.show_punchline,
            bg="#003300", fg="#00FF00", font=("Consolas", 10, "bold"), width=25
        )
        self.punch_btn.grid(row=1, column=0, padx=5, pady=2)
        self.next_btn = tk.Button(
            self.button_frame, text="NEXT JOKE", command=self.show_joke,
            bg="#003300", fg="#00FF00", font=("Consolas", 10, "bold"), width=25
        )
        self.next_btn.grid(row=2, column=0, padx=5, pady=2)
        self.quit_btn = tk.Button(
            self.button_frame, text="QUIT", command=root.destroy,
            bg="#003300", fg="#00FF00", font=("Consolas", 10, "bold"), width=25
        )
        self.quit_btn.grid(row=3, column=0, padx=5, pady=2)

    def typewriter(self, text, append=False, index=0, delay=25):
        if append:
            current_text = self.dialogue_label.cget("text")
        else:
            current_text = ""
            self.dialogue_label.config(text="")
        if index < len(text):
            self.dialogue_label.config(text=current_text + text[index])
            self.typing_job = self.root.after(delay, lambda: self.typewriter(text, append=True, index=index+1, delay=delay))
        else:
            self.typing_job = None

    def snake_answer(self, setup):
        setup_lower = setup.lower()
        if setup_lower.startswith("why did") or setup_lower.startswith("why should") or setup_lower.startswith("why"):
            return "Why?"
        elif setup_lower.startswith("what happens") or setup_lower.startswith("what does") or setup_lower.startswith("what"):
            return "What?"
        elif setup_lower.startswith("have you"):
            return "Huh?"
        elif setup_lower.startswith("how did") or setup_lower.startswith("how"):
            return "How?"
        else:
            return "Huh?"

    def show_joke(self):
        if os.path.exists("Codec.wav"):
            self.joke_channel.play(self.joke_sfx)

        if self.typing_job:
            self.root.after_cancel(self.typing_job)
        self.dialogue_label.config(text="")
        self.current_joke = random.choice(self.jokes)
        setup, punchline = self.current_joke.split("?")
        self.next_punchline = punchline

        available_faces = [f for f in self.face_images if f not in self.used_faces]
        if not available_faces:
            self.used_faces = []
            available_faces = self.face_images.copy()

        caller_face = random.choice(available_faces)
        self.used_faces.append(caller_face)
        self.caller_face_label.config(image=caller_face)
        self.caller_face_label.image = caller_face
        self.listener_face_label.config(image=self.snake_face)
        self.listener_face_label.image = self.snake_face

        dialogue_text = f"CALLER:\n{setup}?"
        self.typewriter(dialogue_text, append=False)
        self.snake_dynamic_response = self.snake_answer(setup)

    def show_punchline(self):
        if self.current_joke and not self.typing_job:
            if os.path.exists("Laugh.wav"):
                self.laugh_channel.play(self.laugh_sfx)
            punch_text = f"\nSNAKE:\n{self.snake_dynamic_response}\nCALLER:\n{self.next_punchline}"
            self.typewriter(punch_text, append=True, delay=35)

if __name__ == "__main__":
    root = tk.Tk()
    app = CodecJokes(root)

    root.mainloop()
