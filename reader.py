import subprocess
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "env", "__pycache__",
             "dist", "build", ".next", "target", "vendor", ".idea", "site-packages"}
CODE_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cpp", ".c",
            ".go", ".rs", ".cs", ".php", ".kt"}
HINTS = ("app", "main", "server", "index", "api", "route", "model",
         "train", "core", "service")
MAX_FILES = 4
MAX_CHARS = 3000


def clone_repo(url):
    url = url.strip().rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]
    name = url.split("/")[-1]
    dest = Path("repos") / name
    if not dest.exists():
        Path("repos").mkdir(exist_ok=True)
        subprocess.run(["git", "clone", "--depth", "1", url + ".git", str(dest)],
                       check=True, capture_output=True)
    return dest


def pick_files(root):
    cands = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.suffix not in CODE_EXT:
            continue
        size = p.stat().st_size
        if size < 200 or size > 200_000:
            continue
        score = -len(rel.parts)
        if any(h in p.stem.lower() for h in HINTS):
            score += 3
        if "test" in p.stem.lower():
            score -= 5
        score += min(size, 6000) / 3000
        cands.append((score, p))
    cands.sort(key=lambda x: -x[0])
    return [p for _, p in cands[:MAX_FILES]]


def load_repo(url):
    root = clone_repo(url)
    readme = ""
    for n in ("README.md", "readme.md", "README.rst", "README.txt", "README"):
        f = root / n
        if f.exists():
            readme = f.read_text(encoding="utf-8", errors="ignore")[:MAX_CHARS]
            break
    files = []
    for p in pick_files(root):
        text = p.read_text(encoding="utf-8", errors="ignore")[:MAX_CHARS]
        files.append((str(p.relative_to(root)).replace("\\", "/"), text))
    return {"name": root.name, "readme": readme, "files": files}


if __name__ == "__main__":
    import sys
    d = load_repo(sys.argv[1])
    print(d["name"], "| README chars:", len(d["readme"]))
    for path, c in d["files"]:
        print(" -", path, len(c))