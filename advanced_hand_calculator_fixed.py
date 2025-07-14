
import cv2
import mediapipe as mp
import time
import os  # For Mac's voice output

# ✅ Use working camera index and AVFoundation backend
cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

expression = ""
result = ""
last_time = 0
cooldown = 1  # seconds

def get_finger_states(hand_landmarks):
    tips = [4, 8, 12, 16, 20]
    states = []

    # Thumb
    if hand_landmarks.landmark[tips[0]].x < hand_landmarks.landmark[tips[0]-1].x:
        states.append(1)
    else:
        states.append(0)

    # Other 4 fingers
    for i in range(1, 5):
        if hand_landmarks.landmark[tips[i]].y < hand_landmarks.landmark[tips[i]-2].y:
            states.append(1)
        else:
            states.append(0)

    return states

def recognize_gesture(states):
    if states == [0, 1, 0, 0, 0]: return "1"
    elif states == [0, 1, 1, 0, 0]: return "2"
    elif states == [0, 1, 1, 1, 0]: return "3"
    elif states == [0, 1, 1, 1, 1]: return "4"
    elif states == [0, 1, 0, 1, 1]: return "5"
    elif states == [1, 1, 1, 1, 1]: return "="
    elif states == [1, 0, 0, 0, 1]: return "*"
    elif states == [1, 1, 0, 0, 0]: return "+"
    elif states == [0, 0, 0, 0, 0]: return "C"
    elif states == [0, 0, 0, 1, 1]: return "-"
    elif states == [1, 1, 0, 0, 1]: return "/"
    elif states == [1, 0, 1, 1, 1]: return "7"
    elif states == [1, 1, 1, 0, 1]: return "8"
    elif states == [1, 1, 1, 1, 0]: return "9"
    elif states == [0, 1, 1, 1, 1]: return "6"
    else: return ""

while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            fingers = get_finger_states(hand_landmarks)
            gesture = recognize_gesture(fingers)

            current_time = time.time()
            if gesture and (current_time - last_time > cooldown):
                if gesture == "C":
                    expression = ""
                    result = ""
                elif gesture == "=":
                    try:
                        result = str(eval(expression))
                        os.system(f"say The answer is {result}")
                        expression = result
                    except:
                        result = "Error"
                        expression = ""
                else:
                    expression += gesture
                    result = ""
                last_time = current_time

            cv2.putText(frame, f'Gesture: {gesture}', (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.putText(frame, f'Exp: {expression}', (10, 150),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

    if result:
        cv2.putText(frame, f'Result: {result}', (10, 220),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)

    cv2.imshow("Hand Calculator", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
