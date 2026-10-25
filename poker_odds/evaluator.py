"""Turn 7 cards into a single number: bigger number = better poker hand.

Score layout (an integer):
    category (0-8) in the high bits, then up to 5 "tie-breaker" ranks.
Two hands are compared simply by comparing their scores. Equal scores = a tie.

Categories:
    0 high card   1 pair   2 two pair   3 three of a kind   4 straight
    5 flush       6 full house   7 four of a kind   8 straight flush
"""

CATEGORY_NAMES = [
    "High card", "Pair", "Two pair", "Three of a kind", "Straight",
    "Flush", "Full house", "Four of a kind", "Straight flush",
]


def _pack(category, ranks):
    """Pack the category and tie-breaker ranks into one integer (4 bits per rank)."""
    score = category
    for i in range(5):
        score = (score << 4) | (ranks[i] if i < len(ranks) else 0)
    return score


def category_name(score: int) -> str:
    return CATEGORY_NAMES[score >> 20]


def _best_straight_high(rank_set):
    """Highest card of the best straight in rank_set, or 0 if none. Ace can be low (A-2-3-4-5)."""
    mask = 0
    for r in rank_set:
        mask |= 1 << r
    if 14 in rank_set:
        mask |= 1 << 1                       # ace also counts as a 1
    for high in range(14, 4, -1):
        if (mask >> (high - 4)) & 31 == 31:  # five ranks in a row ending at `high`
            return high
    return 0


def evaluate_7(cards) -> int:
    """Best 5-card hand score from 7 cards (works for 5 or 6 cards too)."""
    counts = [0] * 15                        # how many of each rank
    by_suit = [[], [], [], []]               # ranks grouped by suit
    for rank, suit in cards:
        counts[rank] += 1
        by_suit[suit].append(rank)

    # --- Flush and straight flush -------------------------------------------
    flush_ranks = None
    for ranks in by_suit:
        if len(ranks) >= 5:
            flush_ranks = sorted(ranks, reverse=True)
            high = _best_straight_high(flush_ranks)
            if high:
                return _pack(8, [high])
            break

    # Groups sorted by (how many, rank): quads/trips/pairs come before singles.
    groups = sorted(((c, r) for r, c in enumerate(counts) if c), reverse=True)
    top_count = groups[0][0]

    # --- Four of a kind -----------------------------------------------------
    if top_count == 4:
        quad = groups[0][1]
        kicker = max(r for c, r in groups[1:])
        return _pack(7, [quad, kicker])

    # --- Full house ---------------------------------------------------------
    if top_count == 3 and len(groups) > 1 and groups[1][0] >= 2:
        return _pack(6, [groups[0][1], groups[1][1]])

    # --- Flush --------------------------------------------------------------
    if flush_ranks:
        return _pack(5, flush_ranks[:5])

    # --- Straight -----------------------------------------------------------
    high = _best_straight_high([r for c, r in groups])
    if high:
        return _pack(4, [high])

    # --- Three of a kind ----------------------------------------------------
    if top_count == 3:
        kickers = [r for c, r in groups[1:]]
        return _pack(3, [groups[0][1]] + kickers[:2])

    # --- Two pair -----------------------------------------------------------
    if top_count == 2 and groups[1][0] == 2:
        kicker = max(r for c, r in groups[2:]) if len(groups) > 2 else 0
        return _pack(2, [groups[0][1], groups[1][1], kicker])

    # --- One pair -----------------------------------------------------------
    if top_count == 2:
        kickers = [r for c, r in groups[1:]]
        return _pack(1, [groups[0][1]] + kickers[:3])

    # --- High card ----------------------------------------------------------
    return _pack(0, [r for c, r in groups][:5])
