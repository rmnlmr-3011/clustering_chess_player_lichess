# Code relatif à l'ouverture, notamment la normalisation du code ECO et le mapping vers la famille d'ouverture.

from __future__ import annotations

import re


ECO_PATTERN = re.compile(r"^[A-E]\d{2}$")


# Taxonomie finale retenue pour le projet
OPENING_FAMILY_BY_ECO_RULES: list[tuple[str, int, int, str]] = [
    # A
    ("A", 0, 0, "Irregular Openings"),
    ("A", 1, 1, "Nimzovich–Larsen Attack"),
    ("A", 2, 3, "Bird’s Opening"),
    ("A", 4, 9, "Réti Opening"),
    ("A", 10, 39, "English Opening"),
    ("A", 40, 49, "Queen's Pawn"),
    ("A", 50, 79, "Benoni & Benko Families"),
    ("A", 80, 99, "Dutch Defense"),

    # B
    ("B", 0, 5, "Alekhine Defense & related starts"),
    ("B", 6, 9, "Modern / Robatsch / Pirc"),
    ("B", 10, 19, "Caro–Kann Defense"),
    ("B", 20, 99, "Sicilian"),

    # C
    ("C", 0, 19, "French Defense"),
    ("C", 20, 29, "King’s Pawn Games / Bishop’s Opening / Vienna"),
    ("C", 30, 39, "King’s Gambit"),
    ("C", 40, 40, "King’s Knight Opening & sidelines"),
    ("C", 41, 41, "Philidor's Defence"),
    ("C", 42, 43, "Petrov Defense"),
    ("C", 44, 45, "Scotch Game & related branches"),
    ("C", 46, 49, "Three Knights / Four Knights"),
    ("C", 50, 59, "Italian Game & Two Knights Defense"),
    ("C", 60, 99, "Ruy Lopez"),

    # D
    ("D", 0, 5, "Queen’s Pawn Systems"),
    ("D", 6, 69, "Queen’s Gambit / Slav Families"),
    ("D", 70, 79, "Neo-Grünfeld"),
    ("D", 80, 99, "Grünfeld Defense"),

    # E
    ("E", 0, 0, "Early Indian Systems with …e6"),
    ("E", 1, 9, "Catalan Opening"),
    ("E", 10, 11, "Bogo-Indian / Queen’s Pawn branches"),
    ("E", 12, 19, "Queen’s Indian Defense"),
    ("E", 20, 59, "Nimzo-Indian"),
    ("E", 60, 99, "King’s Indian Defense"),
]


def normalize_eco(eco: str | None) -> str | None:
    """
    Normalise un code ECO vers le format canonique 'A00'...'E99'.

    Exemples:
    - 'b12'    -> 'B12'
    - ' B12 '  -> 'B12'
    - None     -> None
    - '??'     -> None
    """
    if eco is None:
        return None

    eco = eco.strip().upper()

    if not ECO_PATTERN.fullmatch(eco):
        return None

    return eco


def map_eco_to_opening_family(eco: str | None) -> str | None:
    """
    Mappe un code ECO vers la famille d'ouverture définie dans la taxonomie du projet.

    Retourne None si:
    - eco est None
    - eco est invalide
    - eco n'entre dans aucune règle (normalement ne devrait pas arriver ici)
    """
    eco_norm = normalize_eco(eco)
    if eco_norm is None:
        return None

    letter = eco_norm[0]
    number = int(eco_norm[1:])

    for rule_letter, start, end, family in OPENING_FAMILY_BY_ECO_RULES:
        if letter == rule_letter and start <= number <= end:
            return family

    return None