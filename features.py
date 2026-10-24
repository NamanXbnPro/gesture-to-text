"""Pose labels from MediaPipe hand landmarks.

Each finger is marked up or down from joint geometry, not from a network.
A word is returned only when the up/down pattern matches one pose exactly.
Anything in between returns "" so two gestures are not swapped.
"""
import numpy as np

# (mcp, pip, dip, tip) — thumb uses CMC as the first joint.
CHAINS = {
    "thumb": (1, 2, 3, 4),
    "index": (5, 6, 7, 8),
    "middle": (9, 10, 11, 12),
    "ring": (13, 14, 15, 16),
    "pinky": (17, 18, 19, 20),
}

POSES = {
    "open": {"thumb": 1, "index": 1, "middle": 1, "ring": 1, "pinky": 1},
    "high": {"thumb": 1, "index": 1, "middle": 1, "ring": 1, "pinky": 0},
    "four": {"thumb": 0, "index": 1, "middle": 1, "ring": 1, "pinky": 1},
    "three": {"thumb": 0, "index": 1, "middle": 1, "ring": 1, "pinky": 0},
    "aim": {"thumb": 1, "index": 1, "middle": 1, "ring": 0, "pinky": 0},
    "peace": {"thumb": 0, "index": 1, "middle": 1, "ring": 0, "pinky": 0},
    "love": {"thumb": 1, "index": 1, "middle": 0, "ring": 0, "pinky": 1},
    "letter_l": {"thumb": 1, "index": 1, "middle": 0, "ring": 0, "pinky": 0},
    "rock": {"thumb": 0, "index": 1, "middle": 0, "ring": 0, "pinky": 1},
    "point": {"thumb": 0, "index": 1, "middle": 0, "ring": 0, "pinky": 0},
    "yo": {"thumb": 1, "index": 0, "middle": 0, "ring": 0, "pinky": 1},
    "thumbs_up": {"thumb": 1, "index": 0, "middle": 0, "ring": 0, "pinky": 0},
    "pinky": {"thumb": 0, "index": 0, "middle": 0, "ring": 0, "pinky": 1},
    "fist": {"thumb": 0, "index": 0, "middle": 0, "ring": 0, "pinky": 0},
}


def _cos(u, v) -> float:
    return float(np.dot(u, v) / ((np.linalg.norm(u) + 1e-6) * (np.linalg.norm(v) + 1e-6)))


def _hand_frame(lm_xy):
    pts = np.asarray(lm_xy, dtype=np.float64).reshape(21, 2)
    rel = pts - pts[0]
    rel[:, 1] *= -1.0
    scale = float(np.linalg.norm(rel[9])) + 1e-6
    return rel / scale


def finger_up(rel, name: str) -> bool:
    """True only when the finger is both straight and reaching out."""
    mcp, pip, dip, tip = CHAINS[name]
    bones = (rel[pip] - rel[mcp], rel[dip] - rel[pip], rel[tip] - rel[dip])
    straight = 0.5 * (_cos(bones[0], bones[1]) + _cos(bones[1], bones[2]))
    tip_reach = float(np.linalg.norm(rel[tip]))
    pip_reach = float(np.linalg.norm(rel[pip]))
    if name == "thumb":
        # Thumb sticks out to the side. Compare with the index knuckle,
        # not with "up", so a rotated hand still counts.
        side = float(np.linalg.norm(rel[4] - rel[5]))
        return straight > 0.45 and side > 0.55 and tip_reach > 0.7
    return straight > 0.55 and tip_reach > pip_reach + 0.35 and tip_reach > 1.35


def classify_pose(lm_xy) -> str:
    rel = _hand_frame(lm_xy)
    # Thumb tip touching the index tip, other three fingers up: the "nice" pinch.
    # Checked first so a curled index is not read as pointing or as an open palm.
    pinch = float(np.linalg.norm(rel[4] - rel[8]))
    three_up = all(finger_up(rel, name) for name in ("middle", "ring", "pinky"))
    index_up = finger_up(rel, "index")
    if pinch < 0.55 and three_up and not index_up:
        return "nice"
    state = {name: int(finger_up(rel, name)) for name in CHAINS}
    for pose, pattern in POSES.items():
        if state == pattern:
            return pose
    return ""

