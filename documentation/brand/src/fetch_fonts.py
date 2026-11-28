"""Downloads the brand fonts: web fonts into fonts/fonts.json (Latin and Latin Extended, which holds the
rupee sign) and IBM Plex Sans TTF files into fonts/ttf for outlining the logo. All are open-licence Google Fonts."""
import base64
import json
import re
import urllib.request
from pathlib import Path

FONTS = Path(__file__).resolve().parent / "fonts"
SPECS = {"Bricolage Grotesque": "Bricolage+Grotesque:opsz,wght@12..96,400..800",
         "IBM Plex Sans": "IBM+Plex+Sans:wght@400..700", "Roboto": "Roboto:wght@400..700"}
BROWSER = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"


def get(url, agent=BROWSER):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": agent}), timeout=60).read()


def main():
    out = {}
    for family, spec in SPECS.items():
        css = get(f"https://fonts.googleapis.com/css2?family={spec}&display=block").decode()
        blocks = [b for n, b in re.findall(r"/\* ([\w-]+) \*/\s*(@font-face \{.*?\})", css, re.S) if n in ("latin", "latin-ext")]
        assert blocks, family
        for i, block in enumerate(blocks):
            url = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)", block).group(1)
            data = get(url)
            assert data[:4] == b"wOF2", url
            blocks[i] = block.replace(url, "data:font/woff2;base64," + base64.b64encode(data).decode())
        out[family] = "\n".join(blocks)
    (FONTS / "ttf").mkdir(parents=True, exist_ok=True)
    (FONTS / "fonts.json").write_text(json.dumps(out))
    # a plain user agent makes the service send TTF files
    css = get("https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@500;600;700", "font-fetch").decode()
    for weight, url in re.findall(r"font-weight: (\d+);.*?url\((https://fonts\.gstatic\.com/[^)]+\.ttf)\)", css, re.S):
        (FONTS / "ttf" / f"IBMPlexSans-{weight}.ttf").write_bytes(get(url, "font-fetch"))
    print("fonts saved in", FONTS)


if __name__ == "__main__":
    main()
