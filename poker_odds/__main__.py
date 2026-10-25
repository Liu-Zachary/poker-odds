"""Usage examples:
    python -m poker_odds AsAh KsKh                       # hero vs known villain (Monte Carlo)
    python -m poker_odds AsAh KsKh --board 2c7d9h --exact
    python -m poker_odds AsKs random --board QsJs2d      # vs a random hand
"""
import argparse
import time

from .cards import card_to_str, parse_cards
from .odds import exact_odds, monte_carlo_odds


def main() -> None:
    p = argparse.ArgumentParser(prog="poker_odds", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("hero", help="your two cards, e.g. AsAh")
    p.add_argument("villain", help="opponent's two cards, or the word 'random'")
    p.add_argument("--board", default="", help="0, 3, 4 or 5 community cards, e.g. 2c7d9h")
    p.add_argument("--exact", action="store_true", help="enumerate everything instead of simulating")
    p.add_argument("-n", "--samples", type=int, default=100_000, help="Monte Carlo samples")
    p.add_argument("--seed", type=int, default=None)
    args = p.parse_args()

    hero = parse_cards(args.hero)
    villain = None if args.villain.lower() == "random" else parse_cards(args.villain)
    board = parse_cards(args.board) if args.board else []

    start = time.time()
    if args.exact:
        r = exact_odds(hero, board, villain)
        method = f"exact ({r.total:,} outcomes)"
    else:
        r = monte_carlo_odds(hero, board, villain, n=args.samples, seed=args.seed)
        method = f"Monte Carlo ({r.total:,} samples)"
    elapsed = time.time() - start

    print(f"Hero: {' '.join(map(card_to_str, hero))}   "
          f"Villain: {'random' if villain is None else ' '.join(map(card_to_str, villain))}   "
          f"Board: {' '.join(map(card_to_str, board)) or '-'}")
    print(f"Method: {method} in {elapsed:.2f}s")
    print(f"  Win  {r.win_pct:7.2%}")
    print(f"  Tie  {r.tie_pct:7.2%}")
    print(f"  Lose {r.losses / r.total:7.2%}")
    print(f"  Equity {r.equity:.4f}" + ("" if r.exact else f"  (+/- {1.96 * r.std_error:.4f} at 95% confidence)"))


if __name__ == "__main__":
    main()
