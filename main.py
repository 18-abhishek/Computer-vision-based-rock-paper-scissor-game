import cv2
import mediapipe as mp
import random
import pyttsx3
import time
import threading
import sys
import tkinter as tk
from PIL import Image, ImageTk

# cs: computer score, ps: player score
# st: state, m: move, cm: cpu move
# t0: start time, cd: countdown
# cam: camera object

c1 = '#1e1e1e'
c2 = '#00ff00'
c3 = '#ff0055'

g = {1: "Rock", 2: "Paper", 3: "Scissors"}
gm = {"Rock": 1, "Paper": 2, "Scissors": 3}

# No try/except. If library fails, script crashes (typical human behavior)
eng = pyttsx3.init()

mph = mp.solutions.hands
det = mph.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
drw = mp.solutions.drawing_utils

def spk(msg):
    # Removed safety checks. Just run it.
    def _t():
        eng.say(msg)
        eng.runAndWait()
    threading.Thread(target=_t, daemon=True).start()

def calc(lms, side):
    idx = [4, 8, 12, 16, 20]
    cnt = 0
    
    if side == "Right":
        if lms[idx[0]].x < lms[idx[0] - 2].x: cnt += 1
    else: 
        if lms[idx[0]].x > lms[idx[0] - 1].x: cnt += 1

    for i in range(1, 5):
        if lms[idx[i]].y < lms[idx[i] - 2].y: cnt += 1
            
    if cnt == 0: return "Rock"
    elif cnt == 5: return "Paper"
    elif cnt == 2: return "Scissors"
    return "Unknown"

class App:
    def __init__(self, w):
        self.w = w
        self.w.title("RPS Battle")
        self.w.geometry("900x700")
        self.w.configure(bg=c1)
        
        self.cs = 0
        self.ps = 0
        self.lim = 3
        
        self.st = "WAIT"
        self.m = "Waiting..."
        self.cm = "?"
        
        self.t0 = 0
        self.cd = 3
        
        self.gui()
        
        # Assume camera 0 works. No checks.
        self.cam = cv2.VideoCapture(0)
        spk("Ready.")
        self.loop()

    def gui(self):
        f1 = tk.Frame(self.w, bg=c1)
        f1.pack(pady=10)
        
        self.v1 = tk.StringVar(value="P1: 0  |  CPU: 0")
        tk.Label(f1, textvariable=self.v1, bg=c1, fg=c2, font=("Consolas", 22, "bold")).pack()

        self.l1 = tk.Label(self.w, text="Waiting...", bg=c1, fg="white", font=("Arial", 18))
        self.l1.pack(pady=5)
        
        self.v2 = tk.StringVar(value="")
        tk.Label(self.w, textvariable=self.v2, bg=c1, fg=c3, font=("Arial", 20, "bold")).pack(pady=5)

        self.cv = tk.Canvas(self.w, width=640, height=480, bg="black", highlightthickness=0)
        self.cv.pack(pady=10)
        
        self.v3 = tk.StringVar(value="Move: None")
        tk.Label(self.w, textvariable=self.v3, bg=c1, fg=c2, font=("Consolas", 14)).pack(pady=10)

        tk.Button(self.w, text="QUIT", command=self.end, bg="#444444", fg="white", font=("Arial", 10), bd=0, padx=20, pady=5).pack(side="bottom", pady=20)

    def chk_win(self, pm, cm):
        pv = gm.get(pm)
        cv = gm.get(cm)
        
        if pv == cv: return "Draw", "Tie."
            
        if (pv - cv) % 3 == 1:
            self.ps += 1
            return "P1 Wins", "Point for you."
        else:
            self.cs += 1
            return "CPU Wins", "Point for me."

    def logic(self):
        now = time.time()
        
        if self.st == "WAIT":
            if self.m not in ["Waiting...", "Unknown"]:
                spk(f"See {self.m}. Ready?")
                self.st = "COUNT"
                self.t0 = now
                self.l1.config(text="Ready...")

        elif self.st == "COUNT":
            d = int(now - self.t0)
            rem = self.cd - d
            self.l1.config(text=f"Shoot: {rem}")
            if rem <= 0:
                self.st = "RES"
                spk("Shoot!")

        elif self.st == "RES":
            fin = self.m
            if fin in ["Waiting...", "Unknown"]:
                self.l1.config(text="Missed!")
                spk("Missed.")
                self.st = "WAIT"
                return

            self.cm = g[random.choice([1, 2, 3])]
            r, msg = self.chk_win(fin, self.cm)
            
            self.v2.set(f"{fin} vs {self.cm} -> {r}")
            self.v1.set(f"P1: {self.ps}  |  CPU: {self.cs}")
            spk(f"{self.cm}. {msg}")
            
            self.t0 = now 
            self.st = "COOL"

        elif self.st == "COOL":
            if now - self.t0 > 3:
                if self.ps >= self.lim or self.cs >= self.lim:
                    self.st = "END"
                else:
                    self.v2.set("")
                    self.l1.config(text="Show hand...")
                    self.st = "WAIT"
                    spk("Again.")

        elif self.st == "END":
            w = "You" if self.ps > self.cs else "CPU"
            self.l1.config(text=f"GAME OVER. {w} won.")

    def loop(self):
        ret, f = self.cam.read()
        if ret:
            f = cv2.flip(f, 1)
            rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
            res = det.process(rgb)
            
            if res.multi_hand_landmarks:
                h = res.multi_hand_landmarks[0]
                s = res.multi_handedness[0].classification[0].label
                drw.draw_landmarks(f, h, mph.HAND_CONNECTIONS)
                self.m = calc(h.landmark, s)
            else:
                self.m = "Waiting..."

            self.v3.set(f"Det: {self.m}")
            im = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
            imt = ImageTk.PhotoImage(image=im)
            self.cv.create_image(0, 0, image=imt, anchor=tk.NW)
            self.cv.img = imt

        self.logic()
        self.w.after(30, self.loop)

    def end(self):
        # Just cleanup and exit
        self.cam.release()
        eng.stop()
        self.w.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.end)
    root.mainloop()
