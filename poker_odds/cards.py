"""Cards are stored as (rank, suit) pairs.

rank: 2..14   (11=J, 12=Q, 13=K, 14=A)
suit: 0..3    (s, h, d, c)

Text form is two characters, like "As" (ace of spades) or "Td" (ten of diamonds).
"""

RANK_CHARS = "23456789TJQKA"
SUIT_CHARS = "shdc"


def parse_card(text: str):
    """'Kh' -> (13, 1)"""
    text = text.strip()
    if len(text) != 2 or text[0].upper() not in RANK_CHARS or text[1].lower() not in SUIT_CHARS:
        raise ValueError(f"Bad card {text!r}. Use rank + suit, like 'As', 'Td', '7c'.")
    return (RANK_CHARS.index(text[0].upper()) + 2, SUIT_CHARS.index(text[1].lower()))


def parse_cards(text: str):
    """'AsKh7d' or 'As Kh 7d' -> list of cards"""
    text = text.replace(" ", "").replace(",", "")
    if len(text) % 2 != 0:
        raise ValueError(f"Could not read cards from {text!r}")
    return [parse_card(text[i:i + 2]) for i in range(0, len(text), 2)]


def card_to_str(card) -> str:
    return RANK_CHARS[card[0] - 2] + SUIT_CHARS[card[1]]


def full_deck():
    """All 52 cards."""
    return [(r, s) for r in range(2, 15) for s in range(4)]
