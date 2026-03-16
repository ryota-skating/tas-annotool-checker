import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote

INPUT_ROOT = Path("output/html")
OUTPUT_ROOT = Path("output/json")


def extract_segments_from_html(html_path: Path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    container = soup.select_one(
        "#root > div > main > div > div.annotation-section > div > div.frame-based-elements > div"
    )

    if not container:
        print(f"[WARN] container not found: {html_path}")
        return []

    segments = []

    for item in container.find_all("div", class_="segment-item", recursive=False):
        name_el = item.select_one(".segment-name")
        frames_el = item.select_one(".segment-frames")

        if not name_el or not frames_el:
            continue

        label = name_el.get_text(strip=True)

        match = re.search(r"(\d+)\s*-\s*(\d+)", frames_el.get_text())
        if not match:
            continue

        segments.append({
            "label": label,
            "start_frame": int(match.group(1)),
            "end_frame": int(match.group(2)),
        })

    return segments


def extract_video_title(html_path: Path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")
    video_el = soup.select_one("#root > div > main > div > div.video-section > div > div > video")

    src = video_el["src"]
    path = urlparse(src).path
    name = Path(path).stem
    decoded = unquote(name)
    return decoded


def extract_metadata(html_path: Path):
    """
    output/html/{username}/{username}_{number}.html
    から username と number を抽出
    """

    username = html_path.parent.name

    match = re.match(rf"{re.escape(username)}_(\d+)\.html$", html_path.name)
    if not match:
        raise ValueError(f"Invalid filename format: {html_path}")

    number = int(match.group(1))

    video_title = extract_video_title(html_path)

    return {
        "username": username,
        "title": video_title,
        "html": str(html_path),
        "number": number
    }


def convert_all():
    for html_path in sorted(INPUT_ROOT.glob("*/*.html")):
        segments = extract_segments_from_html(html_path)
        metadata = extract_metadata(html_path)

        data = {
            "metadata": metadata,
            "segments": segments
        }

        # htmlからjsonパスへ変換
        relative = html_path.relative_to(INPUT_ROOT)
        json_path = OUTPUT_ROOT / relative.with_suffix(".json")

        json_path.parent.mkdir(parents=True, exist_ok=True)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[OK] {json_path}")


if __name__ == "__main__":
    convert_all()