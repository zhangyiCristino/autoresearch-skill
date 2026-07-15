from pathlib import Path

Path(__file__).resolve().parents[1].joinpath("EXECUTED").write_text(
    "This marker proves inspected code was executed.", encoding="utf-8"
)
