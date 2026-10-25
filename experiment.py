"""How fast does Monte Carlo error shrink as we add samples?

Uses a turn situation where the exact answer can be computed, then runs the simulation
many times at each sample size and measures the average distance from the exact answer.
Theory says the error should drop by about half each time samples go up 4x (error ~ 1/sqrt(n)).
Run:  python experiment.py
"""
import math
import random

from poker_odds import exact_equity, monte_carlo_equity, parse_cards

HERO = parse_cards("Ah Kh")
BOARD = parse_cards("Qh 7h 2c 9d")          # turn: a nut-flush draw plus overcards
SAMPLE_SIZES = [100, 400, 1600, 6400, 25600]
TRIALS = 40                                  # repeat each size this many times


def main() -> None:
    truth = exact_equity(HERO, BOARD).equity
    print(f"Exact equity for Ah Kh on Qh 7h 2c 9d: {truth:.4f}\n")
    print(f"{'samples':>8} {'avg abs error':>14} {'error x sqrt(n)':>16}")

    rng = random.Random(1)
    rows = []
    for n in SAMPLE_SIZES:
        errors = [abs(monte_carlo_equity(HERO, BOARD, n, rng=rng).equity - truth) for _ in range(TRIALS)]
        avg = sum(errors) / len(errors)
        rows.append((n, avg))
        print(f"{n:>8} {avg:>14.5f} {avg * math.sqrt(n):>16.4f}")

    # If error ~ 1/sqrt(n), then (error x sqrt(n)) should stay roughly constant.
    slope = (math.log(rows[-1][1]) - math.log(rows[0][1])) / (math.log(rows[-1][0]) - math.log(rows[0][0]))
    print(f"\nFitted slope of log(error) vs log(n): {slope:.2f}  (theory: -0.50)")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        ns = [r[0] for r in rows]
        errs = [r[1] for r in rows]
        plt.figure(figsize=(6, 4))
        plt.loglog(ns, errs, "o-", label="measured error")
        plt.loglog(ns, [errs[0] * math.sqrt(ns[0] / n) for n in ns], "--", label="1/sqrt(n) reference")
        plt.xlabel("Monte Carlo samples (n)")
        plt.ylabel("average absolute error")
        plt.title("Monte Carlo error vs sample size")
        plt.legend()
        plt.tight_layout()
        plt.savefig("error_vs_samples.png", dpi=150)
        print("Saved plot to error_vs_samples.png")
    except ImportError:
        print("(Install matplotlib to also save a plot: pip install matplotlib)")


if __name__ == "__main__":
    main()
