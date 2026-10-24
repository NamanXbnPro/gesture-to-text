"""Live gesture -> text.

Finger up/down is measured from the hand landmarks. A word is added only when
the pattern matches one pose exactly, for several frames in a row.

    pip install -r requirements.txt
    python recognize.py

Keys: q quit, c clear, space insert the current word, t toggles speech.
"""
from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
import threading

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from features import classify_pose

GESTURE_TEXT = {
    "open": "hello",
    "high": "high",
    "four": "four",
    "three": "three",
    "aim": "aim",
    "peace": "peace",
    "love": "love",
    "letter_l": "L",
    "rock": "rock",
    "point": "pointing",
    "yo": "yo",
    "thumbs_up": "ok",
    "pinky": "washroom",
    "fist": "fist",
    "nice": "nice",
}

HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20),
    (5, 9), (9, 13), (13, 17),
)


def speak(text: str) -> None:
    def _run():
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass
    threading.Thread(target=_run, daemon=True).start()


def draw_hand(frame, landmarks):
    h, w = frame.shape[:2]
    pts = [(int(p.x * w), int(p.y * h)) for p in landmarks]
    for a, b in HAND_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], (80, 200, 120), 2, cv2.LINE_AA)
    for x, y in pts:
        cv2.circle(frame, (x, y), 3, (240, 240, 240), -1, cv2.LINE_AA)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="hand_landmarker.task")
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--stable", type=int, default=8)
    args = ap.parse_args()

    task_path = Path(args.task)
    if not task_path.is_file():
        import urllib.request
        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        print(f"Downloading {task_path.name} ...")
        urllib.request.urlretrieve(url, task_path)

    options = vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(task_path)),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6,
    )
    landmarker = vision.HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        raise SystemExit(f"Could not open camera {args.camera}")

    recent = deque(maxlen=args.stable)
    sentence = []
    last_word = None
    timestamp_ms = 0
    speech_on = False
    smooth = None

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))
        timestamp_ms += 33
        result = landmarker.detect_for_video(mp_image, timestamp_ms)

        label = ""
        if result.hand_landmarks:
            lm = result.hand_landmarks[0]
            draw_hand(frame, lm)
            pts = np.array([(p.x, p.y, p.z) for p in lm], dtype=np.float64)
            smooth = pts if smooth is None else 0.55 * smooth + 0.45 * pts
            label = classify_pose(smooth[:, :2])
            if label:
                recent.append(label)
            else:
                recent.clear()
        else:
            recent.clear()
            smooth = None

        if len(recent) == args.stable and len(set(recent)) == 1:
            word = GESTURE_TEXT.get(recent[-1], recent[-1])
            if word != last_word:
                sentence.append(word)
                last_word = word
                if speech_on:
                    speak(word)
        if not label:
            last_word = None

        shown = " ".join(sentence[-12:])
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 72), (20, 20, 20), -1)
        cv2.putText(frame, shown or "(show a hand)", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 2, cv2.LINE_AA)
        cv2.putText(frame, f"pose: {label or '-'}   speech: {'on' if speech_on else 'off'} (t)", (12, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 220, 180), 1, cv2.LINE_AA)
        cv2.imshow("gesture to text", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("c"):
            sentence.clear()
            last_word = None
        if key == ord("t"):
            speech_on = not speech_on
        if key == ord(" ") and label:
            word = GESTURE_TEXT.get(label, label)
            sentence.append(word)
            if speech_on:
                speak(word)

    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()


if __name__ == "__main__":
    main()
