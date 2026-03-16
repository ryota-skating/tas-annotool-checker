import json
import re
from pathlib import Path
from collections import defaultdict

JSON_ROOT = Path("output/json")
REPORT_ROOT = Path("output/report")


def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', str(text)) ]


def load_config():
    with open("config.json") as f:
        return json.load(f)


def load_annotations():
    data = defaultdict(dict)

    for p in sorted(JSON_ROOT.glob("*/*.json"), key=natural_keys):
        with open(p) as f:
            j = json.load(f)

        meta = j["metadata"]
        username = meta["username"]
        number = meta["number"]
        video_title = meta["title"]

        data[(number, video_title)][username] = j["segments"]

    return data


def expand_frames(segments):
    frames = {}
    for s in segments:
        for f in range(s["start_frame"], s["end_frame"] + 1):
            frames[f] = s["label"]
    return frames


def frames_to_segments(frames):
    if not frames:
        return []

    segments = []
    sorted_frames = sorted(frames.keys())

    start = sorted_frames[0]
    prev = start
    label = frames[start]

    for f in sorted_frames[1:]:
        if f != prev + 1 or frames[f] != label:
            segments.append((label, start, prev))
            start = f
            label = frames[f]
        prev = f

    segments.append((label, start, prev))
    return segments


def build_ground_truth(a, b=None):
    fa = expand_frames(a)

    if b is None:
        return frames_to_segments(fa)

    fb = expand_frames(b)

    gt = {}
    for f in set(fa) & set(fb):
        if fa[f] == fb[f]:
            gt[f] = fa[f]

    return frames_to_segments(gt)


def overlap(a_start, a_end, b_start, b_end):
    return max(0, min(a_end, b_end) - max(a_start, b_start) + 1)


def majority_length(start, end):
    length = end - start + 1
    if length <= 5:
        return length
    return max(5, length // 4)


def detect_confusable(target, gt, confusable_groups):
    results = []
    for t_label, ts, te in target:
        for g_label, gs, ge in gt:
            ov = overlap(ts, te, gs, ge)
            if ov == 0:
                continue
            cond1 = ov >= majority_length(gs, ge)
            cond2 = ov >= majority_length(ts, te)
            if not (cond1 or cond2):
                continue
            for group in confusable_groups:
                if t_label in group and g_label in group and t_label != g_label:
                    results.append({
                        "target_label": t_label,
                        "correct_label": g_label,
                        "target_segment": [ts, te],
                        "correct_segment": [gs, ge]
                    })
    return results


def detect_long_segments(target, gt, threshold):
    overflow = []
    multi = []
    for t_label, ts, te in target:
        overlaps = []
        for g_label, gs, ge in gt:
            ov = overlap(ts, te, gs, ge)
            if ov > 0:
                overlaps.append((g_label, gs, ge))
        if not overlaps:
            continue
        if len(overlaps) == 1:
            g_label, gs, ge = overlaps[0]
            extra = (te - ts) - (ge - gs)

            if extra > threshold:
                overflow.append({
                    "label": t_label,
                    "target_segment": [ts, te],
                    "correct_segment": [gs, ge],
                    "extra_frames": extra
                })
        else:
            large_segments = []
            for g_label, gs, ge in overlaps:
                ov = overlap(ts, te, gs, ge)
                if ov >= majority_length(gs, ge):
                    large_segments.append({
                        "label": g_label,
                        "range": [gs, ge]
                    })

            if len(set(l["label"] for l in large_segments)) >= 2:
                multi.append({
                    "label": t_label,
                    "target_segment": [ts, te],
                    "contained_correct_segments": large_segments
                })
    return overflow, multi


def process():
    config = load_config()
    data = load_annotations()
    REPORT_ROOT.mkdir(exist_ok=True)
    reports = defaultdict(lambda: {"annotator": "", "videos": []})
    for (number, video_title), users in data.items():
        for group in config["groups"]:
            group_users = [u for u in group if u in users]
            if len(group_users) < 3:
                continue

            for target in group_users:
                target_segments = users[target]
                if not target_segments:
                    continue
                comparisons = [u for u in group_users if u != target and users[u]]
                # if len(comparisons) < 2:
                #     continue
                gt = build_ground_truth(
                    users[comparisons[0]],
                    users[comparisons[1]] if len(comparisons) == 2 else None
                )
                if not gt:
                    continue
                target_seg = frames_to_segments(expand_frames(target_segments))
                confusable = detect_confusable(
                    target_seg,
                    gt,
                    config["confusable_groups"]
                )

                overflow, multi = detect_long_segments(
                    target_seg,
                    gt,
                    config["long_segment_threshold"]
                )

                if not (confusable or overflow or multi):
                    continue

                reports[target]["annotator"] = target

                reports[target]["videos"].append({
                    "number": number,
                    "title": video_title,
                    "confusable_label": confusable,
                    "long_segment_overflow": overflow,
                    "long_segment_multi_label": multi
                })

    for annotator, report in reports.items():
        out = REPORT_ROOT / f"{annotator}.json"

        with open(out, "w") as f:
            json.dump(report, f, indent=2)


if __name__ == "__main__":
    process()