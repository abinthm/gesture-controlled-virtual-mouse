import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# Screen dimensions
screen_w, screen_h = pyautogui.size()

# Camera setup
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Width
cap.set(4, 480)  # Height

# Control parameters
click_threshold = 30  # Pixel distance for clicks
scroll_threshold = 20  # Pixel movement for scroll
history_length = 5     # Smoothing buffer size
click_cooldown = 0.3   # Seconds between clicks
double_click_interval = 0.5  # Seconds for double-click

# State variables
pos_history = []
last_click_time = 0
prev_index_y = 0
prev_index_x = 0
mode = "move"  # Modes: move, scroll
last_mode_switch_time = 0
mode_switch_cooldown = 1  # Seconds between mode switches

def get_distance(landmark1, landmark2, frame):
    x1, y1 = landmark1.x * frame.shape[1], landmark1.y * frame.shape[0]
    x2, y2 = landmark2.x * frame.shape[1], landmark2.y * frame.shape[0]
    return np.hypot(x1 - x2, y1 - y2)

def is_fist(landmarks, frame):
    # Check if all fingertips are close to the palm
    palm = landmarks[0]
    fingertips = [landmarks[8], landmarks[12], landmarks[16], landmarks[20]]
    return all(get_distance(finger, palm, frame) < click_threshold for finger in fingertips)

while True:
    success, frame = cap.read()
    if not success:
        continue

    # Mirror view
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        landmarks = hand_landmarks.landmark

        # Get key landmarks
        index_tip = landmarks[8]
        thumb_tip = landmarks[4]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        palm = landmarks[0]

        # --- Mouse Movement ---
        mouse_x = np.interp(index_tip.x, [0, 1], [0, screen_w])
        mouse_y = np.interp(index_tip.y, [0, 1], [0, screen_h])
        
        # Smoothing
        pos_history.append((mouse_x, mouse_y))
        if len(pos_history) > history_length:
            pos_history.pop(0)
        
        avg_x = int(sum([x for x, y in pos_history]) / len(pos_history))
        avg_y = int(sum([y for x, y in pos_history]) / len(pos_history))

        if mode == "move":
            pyautogui.moveTo(avg_x, avg_y, duration=0.1)

        # --- Gesture Detection ---
        # Left Click (index + thumb)
        dist_index_thumb = get_distance(index_tip, thumb_tip, frame)
        # Right Click (middle + thumb)
        dist_middle_thumb = get_distance(middle_tip, thumb_tip, frame)
        # Fist detection (now used for mode switching)
        fist = is_fist(landmarks, frame)
        
        # Left Click
        if dist_index_thumb < click_threshold:
            if (time.time() - last_click_time) < double_click_interval:
                pyautogui.doubleClick()
                cv2.putText(frame, "DOUBLE CLICK", (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                pyautogui.click()
                cv2.putText(frame, "LEFT CLICK", (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            last_click_time = time.time()

        # Right Click
        elif dist_middle_thumb < click_threshold:
            pyautogui.rightClick()
            cv2.putText(frame, "RIGHT CLICK", (10, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # --- Mode Switching with Fist Gesture ---
        # Instead of using a fist for drag-and-drop (or double click),
        # we now use it to toggle between "move" and "scroll" modes.
        if fist and (time.time() - last_mode_switch_time) > mode_switch_cooldown:
            if mode == "move":
                mode = "scroll"
            else:
                mode = "move"
            last_mode_switch_time = time.time()
            cv2.putText(frame, f"MODE SWITCHED TO {mode.upper()}", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # --- Scroll Detection ---
        if mode == "scroll":
            current_index_y = index_tip.y * frame.shape[0]
            current_index_x = index_tip.x * frame.shape[1]
            if abs(current_index_y - prev_index_y) > scroll_threshold:
                scroll_amount = int((prev_index_y - current_index_y) / 10)
                pyautogui.scroll(scroll_amount)
            if abs(current_index_x - prev_index_x) > scroll_threshold:
                scroll_amount = int((prev_index_x - current_index_x) / 10)
                pyautogui.hscroll(scroll_amount)
            prev_index_y = current_index_y
            prev_index_x = current_index_x

        # Optional: Comment out or remove the previous gesture-based mode switching:
        # if (get_distance(index_tip, middle_tip, frame) < click_threshold and 
        #     get_distance(middle_tip, ring_tip, frame) < click_threshold and 
        #     (time.time() - last_mode_switch_time) > mode_switch_cooldown):
        #     if mode == "move":
        #         mode = "scroll"
        #     elif mode == "scroll":
        #         mode = "move"
        #     last_mode_switch_time = time.time()

        # Visual Feedback
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        cv2.putText(frame, f"MODE: {mode.upper()}", (10, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    # Mode Toggle (Keyboard Controls)
    key = cv2.waitKey(1)
    if key == ord('m'):  # Move mode
        mode = "move"
    elif key == ord('s'):  # Scroll mode
        mode = "scroll"
    elif key == 27:  # ESC to quit
        break

    cv2.imshow('Gesture Mouse', frame)

# Cleanup
cap.release()
cv2.destroyAllWindows()
