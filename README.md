# Gesture to text using python and trained models

Webcam hand poses are turned into words. One hand, 15 static poses. A word is added only when the fingers match one row exactly. A half-pose is ignored instead of being called the wrong word.

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
- [pip on GeeksforGeeks](https://www.geeksforgeeks.org/python/how-to-install-pip-on-windows/)
- [MediaPipe hand landmarks](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/python)

## Run

```powershell
python recognize.py
```

The first run downloads MediaPipe's hand model (`hand_landmarker.task`) into this folder. Wrong camera: `python recognize.py --camera 1`.

## Controls

- Hold the pose still, palm toward the camera, whole hand in frame.
- `t` turns speech on or off. It starts off. When it is on, each new word is spoken out loud.
- `q` quits.
- `c` clears the sentence.
- `space` inserts the current pose immediately.

The on-screen `pose:` line stays `-` until the fingers match one row of the table. Curl the unused fingers all the way in.

## License

[MIT](LICENSE). Copyright (c) 2026 Naman.

## Files

- `recognize.py` — camera loop. Speech is off until you press `t`.
- `features.py` — decides which fingers are up, then matches a pose.
- `requirements.txt` — opencv-python, mediapipe, numpy, pyttsx3.
- `LICENSE` — MIT license.
