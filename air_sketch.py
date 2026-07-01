"""import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.python.solutions import hands as mp_hands
from mediapipe.python.solutions import drawing_utils as mp_draw
import time
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf.symbol_database")


colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 0, 255), (255, 255, 0)]
color_names = ["RED", "GREEN", "BLUE", "YELLOW", "MAGENTA", "CYAN"]
colorIndex = 0
points = [[] for _ in range(len(colors))]


def create_ui(width, height):
    ui_height = height // 8
    ui = np.zeros((ui_height, width, 3), dtype=np.uint8)

    for y in range(ui_height):
        color = [int(240 * (1 - y/ui_height))] * 3
        cv2.line(ui, (0, y), (width, y), color, 1)

    button_width = min(50, width // (len(colors) + 2))
    for i, color in enumerate(colors):
        x = 10 + i * (button_width + 10)
        cv2.circle(ui, (x + button_width // 2, ui_height // 2), button_width // 2 - 5, color, -1)
        cv2.circle(ui, (x + button_width // 2, ui_height // 2), button_width // 2 - 5, (0, 0, 0), 2)
        cv2.putText(ui, color_names[i][0], (x + button_width // 2 - 5, ui_height // 2 + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    cv2.rectangle(ui, (width - 120, 10), (width - 10, ui_height - 10), (200, 200, 200), -1)
    cv2.rectangle(ui, (width - 120, 10), (width - 10, ui_height - 10), (0, 0, 0), 2)
    cv2.putText(ui, "CLEAR", (width - 105, ui_height // 2 + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    return ui
mpHands = mp_hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp_draw



cap = cv2.VideoCapture(0)
frame_width, frame_height = 640, 480
cap.set(3, frame_width)
cap.set(4, frame_height)

ui = create_ui(frame_width, frame_height)
ui_height = ui.shape[0]
canvas = np.full((frame_height, frame_width, 3), 255, dtype=np.uint8)

def get_point(hand, idx):
    return (int(hand.landmark[idx].x * frame_width),
            int(hand.landmark[idx].y * frame_height))

def finger_up(hand, tip, pip):
    return hand.landmark[tip].y < hand.landmark[pip].y

prev_point = None
min_distance = 5
line_thickness = 3
mode = "DRAW"
prev_time = time.time()


while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = mpHands.process(rgb)

    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            index_tip = get_point(hand, 8)
            middle_tip = get_point(hand, 12)

            index_up = finger_up(hand, 8, 6)
            middle_up = finger_up(hand, 12, 10)

            # Eraser Mode
            if index_up and middle_up:
                mode = "ERASER"
                draw_color = (255, 255, 255)
            elif index_up:
                mode = "DRAW"
                draw_color = colors[colorIndex]
            else:
                prev_point = None
                continue

            if index_tip[1] <= ui_height:
                if index_tip[0] > frame_width - 120:
                    canvas.fill(255)
                else:
                    for i, x in enumerate(range(10, 10 + len(colors) * 60, 60)):
                        if x <= index_tip[0] <= x + 50:
                            colorIndex = i
            else:
                if prev_point is None:
                    prev_point = index_tip
                if np.linalg.norm(np.array(index_tip) - np.array(prev_point)) > min_distance:
                    cv2.line(canvas, prev_point, index_tip, draw_color, line_thickness)
                    prev_point = index_tip

            cv2.circle(frame, index_tip, 5, draw_color, -1)

    output = cv2.addWeighted(frame, 0.6, canvas, 0.4, 0)
    output[:ui_height, :] = ui

    fps = int(1 / (time.time() - prev_time))
    prev_time = time.time()

    cv2.putText(output, f"FPS: {fps}", (10, frame_height - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(output, f"Mode: {mode}", (120, frame_height - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(output, f"Color: {color_names[colorIndex]}", (260, frame_height - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    cv2.imshow("AirSketch Pro", output)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        cv2.imwrite("AirSketch_Output.png", canvas)
        print("Saved as AirSketch_Output.png")
    elif key == ord('+'):
        line_thickness = min(10, line_thickness + 1)
    elif key == ord('-'):
        line_thickness = max(1, line_thickness - 1)

cap.release()
cv2.destroyAllWindows()"""



import cv2
import numpy as np
import time
import warnings
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf.symbol_database")

colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 0, 255), (255, 255, 0)]
color_names = ["RED", "GREEN", "BLUE", "YELLOW", "MAGENTA", "CYAN"]
colorIndex = 0

def create_ui(width, height):
    ui_height = height // 8
    ui = np.zeros((ui_height, width, 3), dtype=np.uint8)
    for y in range(ui_height):
        color = [int(240 * (1 - y/ui_height))] * 3
        cv2.line(ui, (0, y), (width, y), color, 1)

    button_width = min(50, width // (len(colors) + 2))
    for i, color in enumerate(colors):
        x = 10 + i * (button_width + 10)
        cv2.circle(ui, (x + button_width // 2, ui_height // 2), button_width // 2 - 5, color, -1)
        cv2.circle(ui, (x + button_width // 2, ui_height // 2), button_width // 2 - 5, (0, 0, 0), 2)
        cv2.putText(ui, color_names[i][0], (x + button_width // 2 - 5, ui_height // 2 + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

    cv2.rectangle(ui, (width - 120, 10), (width - 10, ui_height - 10), (200, 200, 200), -1)
    cv2.rectangle(ui, (width - 120, 10), (width - 10, ui_height - 10), (0, 0, 0), 2)
    cv2.putText(ui, "CLEAR", (width - 105, ui_height // 2 + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    return ui

# --- Hand Landmarker Setup ---
model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print("Downloading hand tracking model package... please wait...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
    urllib.request.urlretrieve(url, model_path)

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
frame_width, frame_height = 640, 480
cap.set(3, frame_width)
cap.set(4, frame_height)

ui = create_ui(frame_width, frame_height)
ui_height = ui.shape[0]
canvas = np.full((frame_height, frame_width, 3), 255, dtype=np.uint8)

prev_point = None
min_distance = 5
line_thickness = 3
mode = "DRAW"
prev_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    
    # Modern MediaPipe expects an mp.Image object
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    results = detector.detect(mp_image)

    if results.hand_landmarks:
        for hand_landmarks in results.hand_landmarks:
            # Landmark mapping for tips and pips
            it_x, it_y = int(hand_landmarks[8].x * frame_width), int(hand_landmarks[8].y * frame_height)
            index_tip = (it_x, it_y)
            
            middle_tip_y = int(hand_landmarks[12].y * frame_height)
            index_pip_y = int(hand_landmarks[6].y * frame_height)
            middle_pip_y = int(hand_landmarks[10].y * frame_height)

            index_up = it_y < index_pip_y
            middle_up = middle_tip_y < middle_pip_y

            # Eraser Mode
            if index_up and middle_up:
                mode = "ERASER"
                draw_color = (255, 255, 255)
            elif index_up:
                mode = "DRAW"
                draw_color = colors[colorIndex]
            else:
                prev_point = None
                continue

            if it_y <= ui_height:
                if it_x > frame_width - 120:
                    canvas.fill(255)
                else:
                    for i, x in enumerate(range(10, 10 + len(colors) * 60, 60)):
                        if x <= it_x <= x + 50:
                            colorIndex = i
            else:
                if prev_point is None:
                    prev_point = index_tip
                if np.linalg.norm(np.array(index_tip) - np.array(prev_point)) > min_distance:
                    cv2.line(canvas, prev_point, index_tip, draw_color, line_thickness)
                    prev_point = index_tip

            cv2.circle(frame, index_tip, 5, draw_color, -1)

    # Canvas dynamic resizing inside loop
    if canvas.shape[:2] != frame.shape[:2]:
        canvas = cv2.resize(canvas, (frame.shape[1], frame.shape[0]))

    output = cv2.addWeighted(frame, 0.6, canvas, 0.4, 0)

    # UI dynamic scaling inside loop
    if ui.shape[1] != output.shape[1]:
        ui = cv2.resize(ui, (output.shape[1], ui_height))
    output[:ui_height, :] = ui

    fps = int(1 / (time.time() - prev_time))
    prev_time = time.time()

    cv2.putText(output, f"FPS: {fps}", (10, frame_height - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(output, f"Mode: {mode}", (120, frame_height - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(output, f"Color: {color_names[colorIndex]}", (260, frame_height - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    cv2.imshow("AirSketch Pro", output)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        cv2.imwrite("AirSketch_Output.png", canvas)
        print("Saved as AirSketch_Output.png")
    elif key == ord('+'):
        line_thickness = min(10, line_thickness + 1)
    elif key == ord('-'):
        line_thickness = max(1, line_thickness - 1)

cap.release()
cv2.destroyAllWindows()