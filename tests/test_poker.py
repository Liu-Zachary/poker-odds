import random
import unittest
from collections import Counter
from itertools import combinations

from poker_odds import (category_name, evaluate_7, exact_odds, full_deck,
                        monte_carlo_odds, parse_cards)


def reference_5card(cards):
    """Slow, simple, independent 5-card ranking used only to check the fast evaluator."""
    ranks = sorted((r for r, s in cards), reverse=True)
    counts = Counter(ranks)
    shape = sorted(counts.values(), reverse=True)
    by_count = sorted(counts, key=lambda r: (counts[r], r), reverse=True)
    flush = len({s for r, s in cards}) == 1
    uniq = sorted(set(ranks), reverse=True)
    straight_high = 0
    if len(uniq) == 5:
        if uniq[0] - uniq[4] == 4:
            straight_high = uniq[0]
        elif uniq == [14, 5, 4, 3, 2]:
            straight_high = 5
    if straight_high and flush:
        return (8, straight_high)
    if shape == [4, 1]:
        return (7, *by_count)
    if shape == [3, 2]:
        return (6, *by_count)
    if flush:
        return (5, *ranks)
    if straight_high:
        return (4, straight_high)
    if shape == [3, 1, 1]:
        return (3, *by_count)
    if shape == [2, 2, 1]:
        return (2, *by_count)
    if shape == [2, 1, 1, 1]:
        return (1, *by_count)
    return (0, *ranks)


def reference_7card(cards):
    return max(reference_5card(list(c)) for c in combinations(cards, 5))


def hand(text):
    return parse_cards(text)


class TestEvaluator(unittest.TestCase):
    def test_category_ordering(self):
        hands = [
            "2c4d6h8sTd9c3h",        # high card
            "AcAd3h5s9dJc2h",        # pair
            "AcAd3h3s9dJc2h",        # two pair
            "AcAdAh3s9dJc2h",        # trips
            "4c5d6h7s8dKcAh",        # straight
            "2h5h7hJhKh3c4d",        # flush
            "AcAdAh3s3d9c2h",        # full house
            "AcAdAhAs3d9c2h",        # quads
            "9h8h7h6h5hKcAd",        # straight flush
        ]
        scores = [evaluate_7(hand(h)) for h in hands]
        self.assertEqual(scores, sorted(scores))
        self.assertEqual(len(set(scores)), len(scores))
        self.assertEqual(category_name(scores[0]), "High card")
        self.assertEqual(category_name(scores[-1]), "Straight flush")

    def test_wheel_is_lowest_straight(self):
        wheel = evaluate_7(hand("Ac2d3h4s5d9cKh"))
        six_high = evaluate_7(hand("2c3d4h5s6dKcAh"))
        self.assertEqual(category_name(wheel), "Straight")
        self.assertLess(wheel, six_high)

    def test_kickers_decide_pairs(self):
        a = evaluate_7(hand("AcAd9h5s3d2c7h"))
        b = evaluate_7(hand("AhAs8h5d3c2d7s"))
        self.assertGreater(a, b)

    def test_board_plays_is_a_tie(self):
        board = hand("AhKhQhJhTh")
        self.assertEqual(evaluate_7(hand("2c3d") + board), evaluate_7(hand("4c5d") + board))

    def test_matches_independent_reference_on_random_hands(self):
        rng = random.Random(0)
        deck = full_deck()
        for _ in range(20000):
            cards = rng.sample(deck, 7)
            fast, slow = evaluate_7(cards), reference_7card(cards)
            # Compare orderings, not raw numbers: check against a second random hand.
            other = rng.sample(deck, 7)
            self.assertEqual(
                (fast > evaluate_7(other)) - (fast < evaluate_7(other)),
                (slow > reference_7card(other)) - (slow < reference_7card(other)),
            )
            self.assertEqual(fast >> 20, slow[0])      # same category


class TestOdds(unittest.TestCase):
    def test_exact_counts_add_up(self):
        r = exact_odds(hand("AsAh"), hand("2c7d9hTd"), hand("KsKh"))
        self.assertEqual(r.total, 44)                  # 44 possible river cards
        self.assertEqual(r.wins + r.ties + r.losses, 44)

    def test_river_is_deterministic(self):
        r = exact_odds(hand("AsAh"), hand("2c7d9hTdJc"), hand("KsKh"))
        self.assertEqual((r.wins, r.ties, r.losses), (1, 0, 0))

    def test_exact_known_value_on_the_turn(self):
        # Hero has a heart flush draw; villain has a pair of aces. Hero wins only by
        # hitting a heart: 13 hearts - 4 already seen = 9 outs, out of 44 unseen cards.
        r = exact_odds(hand("Ah5h"), hand("2h9hKc7s"), hand("AcAd"))
        self.assertEqual(r.wins, 9)
        self.assertEqual(r.total, 44)

    def test_monte_carlo_agrees_with_exact(self):
        hero, board, villain = hand("AsAh"), hand("2c7d9h"), hand("KsKh")
        exact = exact_odds(hero, board, villain)
        mc = monte_carlo_odds(hero, board, villain, n=40000, seed=1)
        self.assertLess(abs(mc.equity - exact.equity), 4 * mc.std_error + 1e-9)

    def test_pocket_aces_vs_random_preflop(self):
        r = monte_carlo_odds(hand("AsAh"), [], None, n=60000, seed=3)
        self.assertAlmostEqual(r.equity, 0.852, delta=0.01)    # well-known ~85%

    def test_error_shrinks_with_more_samples(self):
        hero, board, villain = hand("AsKs"), hand("QsJs2d9c"), hand("7h7d")
        truth = exact_odds(hero, board, villain).equity

        def rms(n):
            errs = [monte_carlo_odds(hero, board, villain, n=n, seed=s).equity - truth
                    for s in range(60)]
            return (sum(e * e for e in errs) / len(errs)) ** 0.5

        self.assertLess(rms(2000), rms(100))

    def test_duplicate_cards_rejected(self):
        with self.assertRaises(ValueError):
            exact_odds(hand("AsAh"), hand("As7d9h"), hand("KsKh"))


if __name__ == "__main__":
    unittest.main()
