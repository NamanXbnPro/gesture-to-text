# Gesture to text

Webcam hand poses are turned into words. Two hands at once. Each hand is named Hand 1 or Hand 2, drawn in its own colour, and listed in a matching text box on the right. A speech slider for that hand sits on the OpenCV window. It starts off. This is the desktop app, not a browser page.

One-hand version: [gesture-to-text-lite](https://github.com/NamanXbnPro/gesture-to-text-lite)

A word is shown only when the fingers match one row exactly. A half-pose stays a dash instead of being called the wrong word.

| Pose | Fingers up | Word |
|---|---|---|
| Open palm | all five | hello |
| Four plus thumb, pinky in | thumb, index, middle, ring | high |
| Four fingers, thumb in | index, middle, ring, pinky | four |
| Three fingers | index, middle, ring | three |
| Thumb, index, and middle | thumb, index, middle | aim |
| Peace | index, middle | peace |
| I-love-you | thumb, index, pinky | love |
| L shape | thumb, index | L |
| Rock | index, pinky | rock |
| Index only | index | pointing |
| Yo | thumb, pinky | yo |
| Thumbs up | thumb | ok |
| Pinky only | pinky | washroom |
| Fist | none | fist |
| Pinch (thumb and index tips touching, other three up) | middle, ring, pinky | nice |

## Virtual environment

Use a venv so these packages stay separate from the rest of Python.

**Windows (PowerShell)**

```powershell
cd C:\Users\Naman\Documents\gesture-to-text
py -3.12 -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
python recognize.py
```

If activation is blocked, run this once, then try `Activate.ps1` again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Command Prompt uses `env\Scripts\activate.bat` instead of `Activate.ps1`.

**macOS and Linux**

```bash
cd gesture-to-text
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python recognize.py
```

Leave the venv with `deactivate`.

Python itself: [python.org/downloads](https://www.python.org/downloads/). Prefer 3.12 if 3.14 gives you install errors. A short venv walkthrough is on [W3Schools](https://www.w3schools.com/python/python_virtualenv.asp). MediaPipe's hand guide is [here](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/python).

## Run

```powershell
python recognize.py
```

Wrong camera: `python recognize.py --camera 1`.

## Controls

- Hold the pose still, palm toward the camera, whole hand in frame.
- The sliders under the camera window are **Hand 1 speech** and **Hand 2 speech**. Drag a slider to the right to speak that hand only. Leave it left to stay silent.
- `q` quits.

The text box stays `-` until the fingers match one row of the table. Curl the unused fingers all the way in.

## Files

- `recognize.py` — camera window, hand colours, text boxes, and speech sliders.
- `speech.py` — speaks a word only when that hand's slider is on.
- `features.py` — decides which fingers are up, then matches a pose.
- `hand_landmarker.task` — MediaPipe hand model. Keep it next to `recognize.py`.
- `requirements.txt` — `opencv-python`, `mediapipe`, `numpy`, `pyttsx3`.

Speech uses the computer's own voice. On Windows that is the built-in voice. No account or internet speech service is required.
