from src.ingestion.opening import map_eco_to_opening_family, normalize_eco


def run_tests():
    # normalisation
    assert normalize_eco("b12") == "B12"
    assert normalize_eco(" B99 ") == "B99"
    assert normalize_eco(None) is None
    assert normalize_eco("") is None
    assert normalize_eco("Z12") is None
    assert normalize_eco("B1") is None

    # mapping A
    assert map_eco_to_opening_family("A00") == "Irregular Openings"
    assert map_eco_to_opening_family("A01") == "Nimzovich–Larsen Attack"
    assert map_eco_to_opening_family("A03") == "Bird’s Opening"
    assert map_eco_to_opening_family("A20") == "English Opening"
    assert map_eco_to_opening_family("A45") == "Queen's Pawn"
    assert map_eco_to_opening_family("A65") == "Benoni & Benko Families"
    assert map_eco_to_opening_family("A90") == "Dutch Defense"

    # mapping B
    assert map_eco_to_opening_family("B03") == "Alekhine Defense & related starts"
    assert map_eco_to_opening_family("B07") == "Modern / Robatsch / Pirc"
    assert map_eco_to_opening_family("B12") == "Caro–Kann Defense"
    assert map_eco_to_opening_family("B23") == "Sicilian"
    assert map_eco_to_opening_family("B76") == "Sicilian"
    assert map_eco_to_opening_family("B95") == "Sicilian"

    # mapping C
    assert map_eco_to_opening_family("C05") == "French Defense"
    assert map_eco_to_opening_family("C25") == "King’s Pawn Games / Bishop’s Opening / Vienna"
    assert map_eco_to_opening_family("C33") == "King’s Gambit"
    assert map_eco_to_opening_family("C40") == "King’s Knight Opening & sidelines"
    assert map_eco_to_opening_family("C41") == "Philidor's Defence"
    assert map_eco_to_opening_family("C42") == "Petrov Defense"
    assert map_eco_to_opening_family("C45") == "Scotch Game & related branches"
    assert map_eco_to_opening_family("C48") == "Three Knights / Four Knights"
    assert map_eco_to_opening_family("C55") == "Italian Game & Two Knights Defense"
    assert map_eco_to_opening_family("C88") == "Ruy Lopez"

    # mapping D
    assert map_eco_to_opening_family("D02") == "Queen’s Pawn Systems"
    assert map_eco_to_opening_family("D08") == "Queen’s Gambit / Slav Families"
    assert map_eco_to_opening_family("D35") == "Queen’s Gambit / Slav Families"
    assert map_eco_to_opening_family("D68") == "Queen’s Gambit / Slav Families"
    assert map_eco_to_opening_family("D75") == "Neo-Grünfeld"
    assert map_eco_to_opening_family("D85") == "Grünfeld Defense"

    # mapping E
    assert map_eco_to_opening_family("E00") == "Early Indian Systems with …e6"
    assert map_eco_to_opening_family("E04") == "Catalan Opening"
    assert map_eco_to_opening_family("E11") == "Bogo-Indian / Queen’s Pawn branches"
    assert map_eco_to_opening_family("E15") == "Queen’s Indian Defense"
    assert map_eco_to_opening_family("E32") == "Nimzo-Indian"
    assert map_eco_to_opening_family("E58") == "Nimzo-Indian"
    assert map_eco_to_opening_family("E76") == "King’s Indian Defense"

    # robustesse
    assert map_eco_to_opening_family(" b12 ") == "Caro–Kann Defense"
    assert map_eco_to_opening_family(None) is None
    assert map_eco_to_opening_family("") is None
    assert map_eco_to_opening_family("???") is None

    print("Tous les tests opening.py sont passés.")


if __name__ == "__main__":
    run_tests()