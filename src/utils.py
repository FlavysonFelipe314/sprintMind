from pathlib import Path


def read_file(path: str) -> str:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    return file_path.read_text(encoding="utf-8", errors="ignore")


def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)


def safe_filename(name: str) -> str:
    return (
        name.replace("\\", "_")
        .replace("/", "_")
        .replace(":", "_")
        .replace(" ", "_")
        .lower()
    )