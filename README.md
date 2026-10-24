# Gesture to text

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
- `s` toggles speech ON/OFF. Speech starts OFF; the camera window shows its status.
- `q` quits.
- `c` clears the sentence.
- `space` inserts the current pose immediately.

The on-screen `pose:` line stays `-` until the fingers match one row of the table. Curl the unused fingers all the way in. That is what stops peace being read as hello, or yo being read as thumbs up.

## Files

- `recognize.py` — camera loop.
- `features.py` — decides which fingers are up, then matches a pose.
- `hand_landmarker.task` — MediaPipe hand model. Keep it next to `recognize.py`.
- `requirements.txt` — `opencv-python`, `mediapipe`, `numpy`.

## Optional speech output

Install the updated requirements, run the app, then press **S** with the camera window focused. Accepted words (including Space inserts) are spoken only while speech is ON. Holding the same pose does not repeatedly speak it. Switching ON does not read old sentence text; show a new pose, release and repeat it, or press Space. Switching OFF stops speech and discards queued words.

Speech uses the local system voice through `pyttsx3`; no online speech service is needed. A separate process keeps the camera responsive. At most three words wait behind the current utterance; excess words are skipped if gestures arrive faster than speech.

On Windows, the built-in SAPI5 voice is used. On Linux, install the system speech engine if needed: `sudo apt install espeak-ng libespeak1`. On macOS, if the backend reports a missing bridge, install `pyobjc` in your virtual environment. If speech fails, the camera keeps running, the status shows ERROR, and details appear in the terminal. Press S to retry after fixing the dependency.

`speech.py` manages the optional voice process.
