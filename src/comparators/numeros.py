from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Optional


@dataclass
class ResultadoNumero:
    pontos: list[str]
    nota: float

    def formatado(self) -> list[str]:
        return self.pontos + [f"{self.nota:.2f}".replace(".", ",")]


def _normalize_numeric(value: str) -> Optional[Decimal]:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None

    cleaned = cleaned.replace("\u2212", "-").replace("\u00a0", "")
    prefix = ""
    if cleaned[0] in "+-":
        prefix = cleaned[0]
        cleaned = cleaned[1:]
    cleaned = cleaned.replace(" ", "").replace("_", "").replace("'", "")
    if not cleaned:
        return None

    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "")
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    else:
        cleaned = cleaned.replace(",", ".")

    if cleaned.count(".") > 1:
        parts = cleaned.split(".")
        cleaned = "".join(parts[:-1]) + "." + parts[-1]

    candidate = prefix + cleaned
    if candidate in {"+", "-", ".", ""}:
        return None
    try:
        return Decimal(candidate)
    except InvalidOperation:
        return None


def _is_int_like(number: Decimal) -> bool:
    return number == number.to_integral_value()


def _format_score(value: float) -> str:
    if value < 0:
        value = 0.0
    if value > 1:
        value = 1.0
    return f"{value:.2f}".replace(".", ",")


def comparar(v1: str, v2: str) -> ResultadoNumero:
    pontos = ["0,0"] * 4
    nota = 0.0

    n1 = _normalize_numeric(v1)
    n2 = _normalize_numeric(v2)

    if n1 is None or n2 is None:
        return ResultadoNumero(pontos, nota)

    if n1 == n2:
        nota += 1.0
        pontos[0] = "1,0"

    diff = abs(n1 - n2)
    scale = max(abs(n1), abs(n2), Decimal("1"))

    if _is_int_like(n1) and _is_int_like(n2):
        tolerance = Decimal("5")
    else:
        tolerance = max(scale * Decimal("0.05"), Decimal("0.01"))
    ratio_abs = min(diff / tolerance, Decimal("1")) if tolerance else Decimal("1")
    score_abs = float(Decimal("1") - ratio_abs)
    score_abs = max(0.0, min(1.0, score_abs))
    nota += score_abs
    pontos[1] = _format_score(score_abs)

    ratio_rel = min(diff / scale, Decimal("1")) if scale else Decimal("0")
    score_rel = float(Decimal("1") - ratio_rel)
    score_rel = max(0.0, min(1.0, score_rel))
    nota += score_rel
    pontos[2] = _format_score(score_rel)

    try:
        if _is_int_like(n1) and _is_int_like(n2):
            same_bucket = diff <= 1
        else:
            precision = Decimal("0.01") if scale <= Decimal("1000") else Decimal("0.1")
            q1 = n1.quantize(precision, rounding=ROUND_HALF_UP)
            q2 = n2.quantize(precision, rounding=ROUND_HALF_UP)
            same_bucket = q1 == q2
    except InvalidOperation:
        same_bucket = False

    score_bucket = 1.0 if same_bucket else 0.0
    nota += score_bucket
    pontos[3] = _format_score(score_bucket)

    return ResultadoNumero(pontos, nota)
