"""Two ways to answer "how often does my hand win?"

1. exact_odds       : look at EVERY possible way the rest of the hand can play out
                      and count. Always correct, but slow when many cards are unknown.
2. monte_carlo_odds : deal the unknown cards randomly N times and count. Fast, but
                      the answer is a little off, and the error shrinks as N grows.

If `villain` is None, the opponent holds a random hand, so we also average over
every possible opponent hand.
"""
import math
import random
from dataclasses import dataclass
from itertools import combinations
from typing import List, Optional, Tuple

from .cards import card_to_str, full_deck
from .evaluator import evaluate_7

Card = Tuple[int, int]


@dataclass
class Result:
    wins: float
    ties: float
    losses: float
    total: int
    exact: bool

    @property
    def win_pct(self) -> float:
        return self.wins / self.total

    @property
    def tie_pct(self) -> float:
        return self.ties / self.total

    @property
    def equity(self) -> float:
        """Win probability counting a tie as half a win."""
        return (self.wins + 0.5 * self.ties) / self.total

    @property
    def std_error(self) -> float:
        """Standard error of the equity estimate (0 for exact results).

        Uses the plain binomial formula sqrt(p(1-p)/n), a slight overestimate because
        ties are scored 0.5. It's the number that shrinks like 1/sqrt(n).
        """
        if self.exact:
            return 0.0
        p = self.equity
        return math.sqrt(p * (1 - p) / self.total)


def _check_inputs(hero, board, villain):
    cards = list(hero) + list(board) + (list(villain) if villain else [])
    if len(hero) != 2:
        raise ValueError("Hero needs exactly 2 hole cards.")
    if villain is not None and len(villain) != 2:
        raise ValueError("Villain needs exactly 2 hole cards (or None for a random hand).")
    if len(board) not in (0, 3, 4, 5):
        raise ValueError("Board must have 0, 3, 4, or 5 cards.")
    if len(set(cards)) != len(cards):
        raise ValueError("The same card appears twice: " + " ".join(card_to_str(c) for c in cards))


def _tally(hero, villain, board) -> int:
    """+1 if hero wins, 0 tie, -1 if hero loses, on a fully dealt board."""
    h = evaluate_7(hero + board)
    v = evaluate_7(villain + board)
    return (h > v) - (h < v)


def exact_odds(hero: List[Card], board: List[Card], villain: Optional[List[Card]] = None) -> Result:
    """Enumerate every possible outcome. Slow with many unknown cards:
    known villain hand, preflop = about 1.7 million boards."""
    _check_inputs(hero, board, villain)
    known = set(hero) | set(board) | (set(villain) if villain else set())
    deck = [c for c in full_deck() if c not in known]
    board_missing = 5 - len(board)

    wins = ties = losses = 0
    villain_options = [list(villain)] if villain else [list(v) for v in combinations(deck, 2)]
    for v in villain_options:
        rest = [c for c in deck if c not in v]               # cards still in the deck
        for runout in combinations(rest, board_missing):     # every way to finish the board
            result = _tally(hero, v, board + list(runout))
            if result > 0:
                wins += 1
            elif result == 0:
                ties += 1
            else:
                losses += 1
    return Result(wins, ties, losses, wins + ties + losses, exact=True)


def monte_carlo_odds(hero: List[Card], board: List[Card], villain: Optional[List[Card]] = None,
                     n: int = 100_000, seed: Optional[int] = None) -> Result:
    """Estimate the odds by dealing the unknown cards randomly n times."""
    _check_inputs(hero, board, villain)
    rng = random.Random(seed)
    known = set(hero) | set(board) | (set(villain) if villain else set())
    deck = [c for c in full_deck() if c not in known]
    board_missing = 5 - len(board)
    villain_needed = 0 if villain else 2

    wins = ties = losses = 0
    for _ in range(n):
        draw = rng.sample(deck, villain_needed + board_missing)   # distinct random cards
        v = list(villain) if villain else draw[:2]
        runout = draw[villain_needed:]
        result = _tally(hero, v, board + runout)
        if result > 0:
            wins += 1
        elif result == 0:
            ties += 1
        else:
            losses += 1
    return Result(wins, ties, losses, n, exact=False)
