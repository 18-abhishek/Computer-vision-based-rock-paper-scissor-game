# **Computer Vision-Powered AI Rock Paper Scissors Game**

This is a computer vision-powered Rock, Paper, Scissors game where the player competes against the computer using real-time hand gestures detected via a webcam.

The application uses the MediaPipe library for hand tracking and integrates with a simple Tkinter graphical user interface (GUI) and the pyttsx3 library for voice feedback.

## **Features**

* **Computer Vision:** Utilizes Google's MediaPipe framework for robust, real-time hand landmark detection and gesture recognition.  
* **Real-time Gameplay:** Tracks the player's hand position and gesture throughout the countdown.  
* **Voice Feedback:** Uses Text-to-Speech (TTS) to guide the player through the game states, announce moves, and declare the winner.  
* **Tkinter GUI:** Provides a clean, dark-themed interface to display the camera feed, score, current move, and game status.  
* **First-to-Three Wins:** The game continues until either the player or the computer reaches 3 wins.

## **Prerequisites**

To run this application, you must have Python installed (version 3.7+ recommended) and a working webcam.

The following Python libraries are required:

| Library | Purpose |
| :---- | :---- |
| opencv-python | Capturing video feed from the webcam. |
| mediapipe | Hand tracking and landmark detection. |
| pyttsx3 | Text-to-Speech functionality for announcements. |
| Pillow (PIL) | Handling and converting image frames for Tkinter display. |
| tkinter | Building the graphical user interface (usually built-in with Python). |

## **Installation and Setup**

1. **Clone or Download:** Get the rps\_game.py file to your local machine.  
2. **Install Dependencies:** Open your terminal or command prompt and run the following command to install the required libraries:  
   pip install opencv-python mediapipe pyttsx3 Pillow

3. **Run the Game:** Execute the Python script.  
   python rps\_game.py

## **How to Play**

The game runs in rounds, aiming for a "first to three" victory.

1. **Start:** The application will open the camera feed and announce, "Welcome to Rock Paper Scissors AI\! Show your hand to initiate the game."  
2. **Ready State:** Hold any clear Rock, Paper, or Scissors gesture into the camera view. Once detected, the game transitions to the countdown.  
3. **Countdown:** A 3-second countdown will begin. You should hold your hand gesture steady during this phase.  
4. **Shoot\!:** When the countdown reaches zero (announced by "Shoot\!"), the game locks in your move.  
5. **Result:** The computer randomly chooses a move, the winner is determined, and the result and updated score are announced via speech and displayed on the screen.  
6. **Next Round:** The game waits for you to show a move again to start the next round.  
7. **Game Over:** The first player to reach 3 points wins the match.

### **Recognized Hand Gestures**

The computer vision model recognizes gestures based on the number and position of extended fingers:

| Move | Gesture Description |
| :---- | :---- |
| **Rock** | All fingers are closed (total 0 extended fingers). |
| **Paper** | All five fingers are extended (total 5 extended fingers). |
| **Scissors** | Index and Middle fingers are extended (V-sign), and all other fingers are folded. |



