from __future__ import annotations
from typing import Any
# validacni funkce pro planner, prevadi a overuji vstupni hodnoty -> chybove zpravy

def to_float(value: Any, name: str) -> float:   # prevod na float
    if value is None:
        raise ValueError(f"{name} nesmí být prázdné.")
    if isinstance(value, bool):
        raise ValueError(f"{name} musí být číslo, ne boolean.")
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} musí být číslo.")


def positive(value: Any, name: str) -> float:   # overi ze hodnota je hladne cislo
    x = to_float(value, name)
    if x <= 0:
        raise ValueError(f"{name} musí být > 0.")
    return x


def non_negative(value: Any, name: str) -> float:   # overi ze hodnota je nezaporna
    x = to_float(value, name)
    if x < 0:
        raise ValueError(f"{name} musí být >= 0.")
    return x


def fraction01(value: Any, name: str, *, allow_percent: bool = True, min_value: float = 0.0) -> float:  # validuje frakc iv intervalu [min_value, 1], kdyz allow_percent=True prijme hodnoty jako procenta
    x = to_float(value, name)

    # Pokud uzivatel zadal 21 misto 0.21 (bezna chyba pri zadavani procent), prevedeme automaticky
    if allow_percent and x > 1.0:
        x = x / 100.0

    if not (min_value <= x <= 1.0):
        if allow_percent:
            raise ValueError(
                f"{name} musí být frakce {min_value}..1.0 (např. 0.32) nebo procenta (např. 32).")
        raise ValueError(f"{name} musí být v rozsahu {min_value}..1.0.")
    return x
