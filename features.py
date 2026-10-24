"""Live gesture -> text.

Finger up/down is measured from the hand landmarks. A word is added only when
the pattern matches one pose exactly, for several frames in a row.

    pip install -r requirements.txt
    python recognize.py

Keys: q quit, c clear, space insert the current word, s toggle speech (starts off).
"""
from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from features import classify_pose
from speech import SpeechOutput

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
    ap.add_argument("--stable", type=int, default=10)
    args = ap.parse_args()

    task_path = Path(args.task)
    if not task_path.is_file():
        raise SystemExit(f"Missing {task_path}. Keep hand_landmarker.task next to this script.")

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

    speech = SpeechOutput()
    try:
        while True:
            speech.poll()
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
                pts = np.array([(p.x, p.y) for p in lm], dtype=np.float64)
                label = classify_pose(pts)
                if label:
                    recent.append(label)
                else:
                    recent.clear()
            else:
                recent.clear()

            if len(recent) == args.stable and len(set(recent)) == 1:
                word = GESTURE_TEXT.get(recent[-1], recent[-1])
                if word != last_word:
                    sentence.append(word)
                    speech.say(word)
                    last_word = word
            if not label:
                last_word = None

            shown = " ".join(sentence[-12:])
            cv2.rectangle(frame, (0, 0), (frame.shape[1], 100), (20, 20, 20), -1)
            cv2.putText(frame, shown or "(show a hand)", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 2, cv2.LINE_AA)
            cv2.putText(frame, f"pose: {label or '-'}", (12, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 220, 180), 1, cv2.LINE_AA)
            status = "ERROR (see terminal)" if speech.error else ("ON" if speech.enabled else "OFF")
            cv2.putText(frame, f"Speech: {status} | S: toggle", (12, 88), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 220, 180), 1, cv2.LINE_AA)
            cv2.imshow("gesture to text", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("s"):
                speech.toggle()
            if key == ord("c"):
                sentence.clear()
                last_word = None
            if key == ord(" ") and label:
                word = GESTURE_TEXT.get(label, label)
                sentence.append(word)
                speech.say(word)

    finally:
        speech.close()
        cap.release()
        cv2.destroyAllWindows()
        landmarker.close()


if __name__ == "__main__":
    main()
