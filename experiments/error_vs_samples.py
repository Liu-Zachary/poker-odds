"""Does Monte Carlo error really shrink like 1/sqrt(n)?

Pick a situation where we can compute the exact answer, then run the simulation many
times at different sample sizes and measure how far off it is on average.

Run from the project folder:  python experiments/error_vs_samples.py
Writes:                       experiments/error_vs_samples.png
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from poker_odds import exact_odds, monte_carlo_odds, parse_cards

HERO, BOARD, VILLAIN = parse_cards("AsKs"), parse_cards("QsJs2d"), parse_cards("7h7d")
SAMPLE_SIZES = [100, 300, 1000, 3000, 10000, 30000]
TRIALS = 200            # simulations per sample size


def main() -> None:
    truth = exact_odds(HERO, BOARD, VILLAIN).equity
    print(f"Exact equity: {truth:.5f}")

    rms_errors = []
    for n in SAMPLE_SIZES:
        sq = 0.0
        for seed in range(TRIALS):
            estimate = monte_carlo_odds(HERO, BOARD, VILLAIN, n=n, seed=seed).equity
            sq += (estimate - truth) ** 2
        rms = (sq / TRIALS) ** 0.5
        rms_errors.append(rms)
        print(f"n={n:>6}  RMS error={rms:.5f}   error*sqrt(n)={rms * n ** 0.5:.3f}")

    # If error ~ c / sqrt(n), then error * sqrt(n) should stay roughly constant.
    c = rms_errors[0] * SAMPLE_SIZES[0] ** 0.5
    plt.figure(figsize=(6, 4.2))
    plt.loglog(SAMPLE_SIZES, rms_errors, "o-", label="measured error")
    plt.loglog(SAMPLE_SIZES, [c / n ** 0.5 for n in SAMPLE_SIZES], "--", label=r"$c/\sqrt{n}$ reference")
    plt.xlabel("Monte Carlo samples (n)")
    plt.ylabel("RMS error in equity")
    plt.title("Simulation error shrinks like 1/sqrt(n)")
    plt.legend()
    plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error_vs_samples.png")
    plt.savefig(out, dpi=150)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
