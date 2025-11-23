import cv2
import mediapipe as mp
import random
import pyttsx3
import time
import tkinter as tk
from tkinter import ttk, PhotoImage, Toplevel
from PIL import Image, ImageTk # Used for image display in Tkinter
import threading
import sys

# --- I. Setup MediaPipe and Helper Functions ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.9)
mp_draw = mp.solutions.drawing_utils

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    if engine:
        # Run speech in a separate thread to prevent GUI lockup
        threading.Thread(target=lambda: (engine.say(text), engine.runAndWait())).start()
    else:
        print(f"[Speech]: {text}")

# Helper function to count extended fingers (Robust version)
# (Same as previous version for robustness)
def count_fingers(landmarks, handedness):
    tip_ids = [4, 8, 12, 16, 20]
    fingers = []
    
    # 1. Check Thumb
    if handedness.label == "Right":
        if landmarks[tip_ids[0]].x < landmarks[tip_ids[0] - 2].x:
            fingers.append(1)
        else:
            fingers.append(0)


    else: # Left Hand
        if landmarks[tip_ids[0]].x > landmarks[tip_ids[0] - 1].x:
            fingers.append(1)
        else:
            fingers.append(0)


    # 2. Check 4 Fingers
    for id in range(1, 5):
        if landmarks[tip_ids[id]].y < landmarks[tip_ids[id] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
            
    return fingers

# Helper to determine the move from hand status
def get_rps_move(fingers):
    total_fingers = fingers.count(1)

    if total_fingers == 0:
        return "Rock"
    if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
        return "Scissors"
    if total_fingers == 5:
        return "Paper"   
    else :
        return "Unknown"

# --- II. Tkinter Application Class ---

class RPSGameGUI:
    def __init__(self, master):
        self.master = master
        master.title("AI Rock Paper Scissors")
        master.geometry("800x600")
        master.configure(bg='#282c34') # Dark background for advanced look

        # --- Game Variables ---
        self.c_score = 0
        self.y_score = 0
        self.game_rounds = 3 
        self.game_map = {1: "Rock", 2: "Paper", 3: "Scissors"}
        self.reverse_game_map = {"Rock": 1, "Paper": 2, "Scissors": 3}
        
        self.game_status = "READY" 
        self.your_move = "Waiting..."
        self.computer_move = "..."
        self.last_result = "..."
        self.countdown_start_time = 0
        self.countdown_duration = 3
        self.result_display_duration = 3

        # --- Tkinter StringVars for Dynamic Updates ---
        self.status_var = tk.StringVar(value="Show your hand to start!")
        self.score_var = tk.StringVar(value=f"Score: You {self.y_score} | Computer {self.c_score}")
        self.move_var = tk.StringVar(value=f"Your Move: {self.your_move}")
        self.result_var = tk.StringVar(value="")

        # --- Setup GUI Components ---
        self.setup_styles()
        self.setup_layout()
        
        # --- Camera Setup ---
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.status_var.set("Error: Camera not found.")
            speak("Camera not found. Exiting.")
            master.after(2000, master.destroy)
        else:
            speak("Welcome to Rock Paper Scissors AI! Show your hand to initiate the game.")
            self.run_game_loop()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam') # Use a theme that allows better customization

        # Style for Main Labels (Score, Status)
        style.configure("TLabel", background="#282c34", foreground="#61afef", font=("Arial", 16))
        
        # Style for Status/Result Label (Larger)
        style.configure("Big.TLabel", background="#282c34", foreground="#e06c75", font=("Arial", 24, "bold"))
        
        # Style for Buttons
        style.configure("TButton", background="#56b6c2", foreground="#282c34", font=("Arial", 12, "bold"))

    def setup_layout(self):
        # Header Frame for Score and Move Display
        header_frame = ttk.Frame(self.master, padding="10", style='TLabel')
        header_frame.pack(fill='x', padx=10, pady=10)

        # Score Label
        ttk.Label(header_frame, textvariable=self.score_var, style='TLabel').pack(side='left')
        
        # Move Label
        ttk.Label(header_frame, textvariable=self.move_var, style='TLabel').pack(side='right')

        # Main Status/Result Frame
        status_frame = ttk.Frame(self.master, padding="20", style='TLabel')
        status_frame.pack(fill='x', padx=10, pady=10)
        
        # Main Status Label
        ttk.Label(status_frame, textvariable=self.status_var, style='Big.TLabel', anchor='center').pack(fill='x')
        
        # Result Label
        ttk.Label(status_frame, textvariable=self.result_var, style='Big.TLabel', anchor='center').pack(fill='x')

        # Game Display Canvas (Tkinter can display images here)
        self.display_canvas = tk.Canvas(self.master, width=640, height=480, bg='#000000')
        self.display_canvas.pack(pady=20)
        
        # Footer Frame for Quit Button
        footer_frame = ttk.Frame(self.master, padding="10", style='TLabel')
        footer_frame.pack(fill='x', padx=10, pady=10)
        
        # Quit Button
        ttk.Button(footer_frame, text="QUIT", command=self.close_app, style='TButton').pack(side='right')

    # --- III. Game Loop and Logic ---
    
    def determine_winner(self, computer_int, your_int):
        # Check game logic
        result = "Draw"
        if your_int == computer_int:
            result = "Draw"
        elif (computer_int == 1 and your_int == 2) or \
             (computer_int == 2 and your_int == 3) or \
             (computer_int == 3 and your_int == 1):
            self.y_score += 1
            result = "You Win"
        else:
            self.c_score += 1
            result = "Computer Win"

        # Update and announce everything
        self.score_var.set(f"Score: You {self.y_score} | Computer {self.c_score}")
        self.result_var.set(f"Result: {result}!")
        
        # Announce all inputs and results
        speak(f"You chose {self.your_move}!")
        speak(f"My choice is {self.computer_move}.")
        speak(f"The result is a {result}! The score is now you {self.y_score}, computer {self.c_score}.") 
        
        return result

    def process_game_state(self):
        current_time = time.time()
        
        # 1. READY state
        if self.game_status == "READY":
            if self.your_move != "Waiting..." and self.your_move != "Unknown":
                speak(f"I see your starting move: {self.your_move}. Get ready!")
                self.game_status = "COUNTDOWN"
                self.countdown_start_time = current_time
                self.status_var.set("Get ready! Countdown starting...")

        # 2. COUNTDOWN state
        elif self.game_status == "COUNTDOWN":
            time_left = self.countdown_duration - int(current_time - self.countdown_start_time)
            self.status_var.set(f"Counting Down: {time_left}")
            
            if time_left <= 0:
                self.game_status = "WAITING_FOR_MOVE"
                speak("Shoot!")
                self.status_var.set("SHOOT! Make your final move!")

        # 3. WAITING_FOR_MOVE state
        elif self.game_status == "WAITING_FOR_MOVE":
            if self.your_move != "Waiting..." and self.your_move != "Unknown":
                
                # Lock in the final move and play the round
                computer_int = random.choice([1, 2, 3])
                self.computer_move = self.game_map[computer_int]
                your_int = self.reverse_game_map.get(self.your_move, 0)
                
                if your_int != 0:
                    self.last_result = self.determine_winner(computer_int, your_int)
                    self.game_status = "SHOWING_RESULT"
                    self.countdown_start_time = current_time 
                    self.status_var.set("Round Complete!")
        
        # 4. SHOWING_RESULT state
        elif self.game_status == "SHOWING_RESULT":
            if current_time - self.countdown_start_time > self.result_display_duration:
                # Check for game over condition
                if self.c_score >= self.game_rounds or self.y_score >= self.game_rounds:
                    self.game_status = "GAME_OVER"
                    self.display_game_over()
                    return # Stop the loop
                else:
                    # Reset for the next round
                    self.game_status = "READY"
                    self.your_move = "Waiting..."
                    self.computer_move = "..."
                    self.last_result = "..."
                    self.result_var.set("")
                    self.status_var.set("Show your hand to start!")
                    speak("Next round. Get ready!")

        # Schedule the next process check
        self.master.after(100, self.run_game_loop)


    def run_game_loop(self):
        # 1. Capture and Process Frame
        success, frame = self.cap.read()
        if success:
            frame = cv2.flip(frame, 1) # Flip for natural view
            
            # --- Hand Detection ---
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)
            
            tracked_move = "Waiting..."
            if results.multi_hand_landmarks:
                for hand_lms, handedness_info in zip(results.multi_hand_landmarks, results.multi_handedness):
                    mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)
                    fingers = count_fingers(hand_lms.landmark, handedness_info.classification[0])
                    tracked_move = get_rps_move(fingers)
                self.your_move = tracked_move
            else:
                self.your_move = "Waiting..."
                
            # Update the move variable in the GUI
            self.move_var.set(f"Your Move: {self.your_move}")
            
            # 2. Display Frame in Tkinter
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.tk_image = ImageTk.PhotoImage(image=img)
            self.display_canvas.create_image(0, 0, image=self.tk_image, anchor=tk.NW)

        # 3. Process Game Logic
        self.process_game_state()

    def display_game_over(self):
        final_winner = "You" if self.y_score > self.c_score else "Computer"
        final_message = f"GAME OVER! Winner: {final_winner}!"
        
        self.status_var.set(final_message)
        self.result_var.set(f"Final Score: You {self.y_score} | Computer {self.c_score}")
        
        # Final voice announcement
        speak(f"The game is over. Final score is you {self.y_score} to computer {self.c_score}. The winner is {final_winner}!")
        
        # Display the final image frame for 5 seconds, then allow quit
        self.master.after(5000, lambda: ttk.Button(self.master, text="Exit", command=self.close_app, style='TButton').pack(pady=10))


    def close_app(self):
        if self.cap.isOpened():
            self.cap.release()
        self.master.destroy()
        # Clean up pyttsx3 resources gracefully
        if engine:
            engine.stop()
        sys.exit()


if __name__ == "__main__":
    root = tk.Tk()
    game_gui = RPSGameGUI(root)
    # Ensure the close_app function is called when the window is closed via the X button
    root.protocol("WM_DELETE_WINDOW", game_gui.close_app) 
    root.mainloop()