from pathlib import Path


def abs_path(*segments: str) -> str:
    return str((Path(__file__).parent.parent / Path(*segments)).resolve())
