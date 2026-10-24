"""Pose labels from MediaPipe hand landmarks.

Each finger is marked up or down from joint geometry, not from a network.
A word is returned only when the up/down pattern matches one pose exactly.
Anything in between returns "" so two gestures are not swapped.
"""
import numpy as np

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


def finger_score(rel, name: str) -> float:
    """0 is curled in, 1 is fully extended. Values in between are unsure."""
    mcp, pip, dip, tip = CHAINS[name]
    bones = (rel[pip] - rel[mcp], rel[dip] - rel[pip], rel[tip] - rel[dip])
    straight = 0.5 * (_cos(bones[0], bones[1]) + _cos(bones[1], bones[2]))
    straight_n = float(np.clip((straight + 0.2) / 1.2, 0.0, 1.0))
    tip_reach = float(np.linalg.norm(rel[tip]))
    pip_reach = float(np.linalg.norm(rel[pip]))
    if name == "thumb":
        side = float(np.linalg.norm(rel[4] - rel[5]))
        side_n = float(np.clip((side - 0.25) / 0.7, 0.0, 1.0))
        reach_n = float(np.clip((tip_reach - 0.35) / 0.9, 0.0, 1.0))
        return 0.4 * straight_n + 0.35 * side_n + 0.25 * reach_n
    reach_n = float(np.clip((tip_reach - pip_reach) / 0.9, 0.0, 1.0))
    long_n = float(np.clip((tip_reach - 0.9) / 1.1, 0.0, 1.0))
    return 0.45 * straight_n + 0.35 * reach_n + 0.2 * long_n


def classify_pose(lm_xy) -> str:
    rel = _hand_frame(lm_xy)
    scores = {name: finger_score(rel, name) for name in CHAINS}
    pinch = float(np.linalg.norm(rel[4] - rel[8]))
    if (
        pinch < 0.5
        and scores["middle"] > 0.62
        and scores["ring"] > 0.62
        and scores["pinky"] > 0.62
        and scores["index"] < 0.45
    ):
        return "nice"
    state = {}
    for name, score in scores.items():
        if score >= 0.64:
            state[name] = 1
        elif score <= 0.36:
            state[name] = 0
        else:
            return ""
    for pose, pattern in POSES.items():
        if state == pattern:
            return pose
    return ""
