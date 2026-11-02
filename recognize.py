"""Live gesture to text. Desktop window only.

Up to MAX_HANDS hands. Each keeps a name, a colour, a text box, and a speech slider.
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

MAX_HANDS = 2
WINDOW = "gesture to text"

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

# BGR. Hand 1 green, Hand 2 blue.
HAND_COLORS = (
    (90, 200, 110),
    (230, 160, 70),
    (180, 120, 240),
    (80, 210, 230),
)


def draw_hand(frame, landmarks, color):
    h, w = frame.shape[:2]
    pts = [(int(p.x * w), int(p.y * h)) for p in landmarks]
    for a, b in HAND_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], color, 2, cv2.LINE_AA)
    for x, y in pts:
        cv2.circle(frame, (x, y), 4, color, -1, cv2.LINE_AA)


def compose(frame, cards):
    """Camera on the left, one coloured text box per hand on the right."""
    h, w = frame.shape[:2]
    panel = 280
    canvas = np.zeros((max(h, 86 * MAX_HANDS + 24), w + panel, 3), np.uint8)
    canvas[:] = (18, 22, 18)
    canvas[:h, :w] = frame
    for i in range(MAX_HANDS):
        color = HAND_COLORS[i]
        name = f"Hand {i + 1}"
        word = "-"
        for card in cards:
            if card[1] == name:
                word = card[2]
        y = 16 + i * 86
        cv2.rectangle(canvas, (w + 16, y), (w + panel - 16, y + 74), (28, 34, 28), -1)
        cv2.rectangle(canvas, (w + 16, y), (w + 22, y + 74), color, -1)
        cv2.putText(canvas, name, (w + 34, y + 26), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1, cv2.LINE_AA)
        cv2.putText(canvas, word, (w + 34, y + 58), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (245, 245, 245), 2, cv2.LINE_AA)
    return canvas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="hand_landmarker.task")
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--stable", type=int, default=10)
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
        num_hands=MAX_HANDS,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6,
    )
    landmarker = vision.HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        raise SystemExit(f"Could not open camera {args.camera}")

    cv2.namedWindow(WINDOW, cv2.WINDOW_AUTOSIZE)
    for n in range(1, MAX_HANDS + 1):
        cv2.createTrackbar(f"Hand {n} speech", WINDOW, 0, 1, lambda _v: None)

    tracks = []
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

            hands = list(result.hand_landmarks or [])[:MAX_HANDS]
            wrists = [(lm[0].x, lm[0].y) for lm in hands]
            used = set()
            order = []
            for index, wrist in enumerate(wrists):
                best_i = None
                best_d = 0.18
                for ti, track in enumerate(tracks):
                    if ti in used:
                        continue
                    d = ((track["wrist"][0] - wrist[0]) ** 2 + (track["wrist"][1] - wrist[1]) ** 2) ** 0.5
                    if d < best_d:
                        best_d = d
                        best_i = ti
                if best_i is None and len(tracks) >= MAX_HANDS and any(ti not in used for ti in range(len(tracks))):
                    best_i = min(
                        (ti for ti in range(len(tracks)) if ti not in used),
                        key=lambda ti: ((tracks[ti]["wrist"][0] - wrist[0]) ** 2 + (tracks[ti]["wrist"][1] - wrist[1]) ** 2) ** 0.5,
                    )
                if best_i is None:
                    taken = {t["n"] for t in tracks}
                    number = next(n for n in range(1, MAX_HANDS + 1) if n not in taken)
                    tracks.append({"n": number, "recent": deque(maxlen=args.stable), "wrist": wrist, "said": None})
                    best_i = len(tracks) - 1
                tracks[best_i]["wrist"] = wrist
                used.add(best_i)
                order.append((best_i, index))
            for ti in sorted((i for i in range(len(tracks)) if i not in used), reverse=True):
                tracks.pop(ti)
                order = [(b if b < ti else b - 1, index) for b, index in order]

            labels = []
            any_voice = False
            for n in range(1, MAX_HANDS + 1):
                if cv2.getTrackbarPos(f"Hand {n} speech", WINDOW):
                    any_voice = True
            if any_voice:
                speech.ensure()
            elif speech.enabled:
                speech.close()

            for track_i, hand_i in order:
                track = tracks[track_i]
                lm = hands[hand_i]
                name = f"Hand {track['n']}"
                color = HAND_COLORS[(track["n"] - 1) % len(HAND_COLORS)]
                draw_hand(frame, lm, color)
                pts = np.array([(p.x, p.y) for p in lm], dtype=np.float64)
                pose = classify_pose(pts)
                slot = track["recent"]
                if pose:
                    slot.append(pose)
                else:
                    slot.clear()
                shown = "-"
                if len(slot) == args.stable and len(set(slot)) == 1:
                    shown = GESTURE_TEXT.get(slot[-1], slot[-1])
                voice = cv2.getTrackbarPos(f"{name} speech", WINDOW) == 1
                if shown != "-" and shown != track["said"] and voice:
                    speech.say(shown)
                    track["said"] = shown
                if shown == "-":
                    track["said"] = None
                labels.append((color, name, shown))

            view = compose(frame, labels)
            cv2.imshow(WINDOW, view)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        speech.close()
        cap.release()
        cv2.destroyAllWindows()
        landmarker.close()


if __name__ == "__main__":
    main()
