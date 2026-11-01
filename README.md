# Gesture to text

`python recognize.py` opens the camera window and a local page at http://127.0.0.1:8000. Hand 1 and Hand 2 each keep a colour. The page lists a text box and a speech switch for each. Speech stays off until you turn that hand's switch on. Press Q in the camera window to quit.

One-hand version: [gesture-to-text-lite](https://github.com/NamanXbnPro/gesture-to-text-lite)

Webcam hand poses are turned into words. Up to two hands. A word is shown only when the fingers match one row exactly.

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
cd gesture-to-text
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

Python itself: [python.org/downloads](https://www.python.org/downloads/). Prefer 3.12 if 3.14 gives you install errors.

Guides if you are new to Python:

- [The Python tutorial](https://docs.python.org/3/tutorial/) on python.org
- [Virtual environments](https://docs.python.org/3/library/venv.html) in the official docs
- [Python tutorial on W3Schools](https://www.w3schools.com/python/)
- [Python programming language on GeeksforGeeks](https://www.geeksforgeeks.org/python/python-programming-language-tutorial/)
- [MediaPipe hand landmarks](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/python)

## Run

```powershell
python recognize.py
```

The browser opens http://127.0.0.1:8000. The first run downloads `hand_landmarker.task` if it is not already in the folder. Wrong camera: `python recognize.py --camera 1`.

Press Q in the camera window to quit. Each hand's speech switch is on the web page and starts off.

## License

[MIT](LICENSE). Copyright (c) 2026 Naman.
