# How to explain this project (for you, not for GitHub)

Keep this out of the public repo if you like, or delete it once you know it cold.

## The 30-second version
"I wrote a poker odds calculator two ways. The exact way checks every possible set of
remaining cards, which is always right but gets slow. The simulation deals random cards
many times, which is fast but a little noisy. I measured the noise and showed it shrinks
like 1 over the square root of the number of samples."

## Questions to be ready for

**How does it decide who wins?**
Each 7-card hand gets turned into one integer: the hand category (pair, flush, etc.) in
the high bits, then the tie-breaker ranks. Bigger integer wins, equal integers tie.

**Why is exact enumeration slow?**
The number of cases is a combination count. Preflop against a known hand there are
C(48,5) = 1,712,304 possible boards, and each needs two hand evaluations.

**Why does simulation error shrink like 1/sqrt(n)?**
Each simulated hand is a coin flip with some win probability p. The average of n flips
has standard deviation sqrt(p(1-p)/n). So 4x the samples halves the error.

**What is equity?**
Chance of winning, counting a tie as half a win. It is the expected share of the pot.

**How do you know the evaluator is right?**
I compared it to a second, slow evaluator on thousands of random hands, plus hand-counted
cases (for example, a flush draw on the turn has 9 outs out of 44 cards).

**What would you improve?**
Speed up the exact method (precomputed lookup tables, or exploiting suit symmetry),
support more than two players, and use variance reduction in the simulation.

## Do this before listing it
1. Read `evaluator.py` and `odds.py` top to bottom until nothing is mysterious.
2. Re-type `monte_carlo_odds` from memory in a blank file.
3. Change something and predict the result first (for example, a different board).
4. Say the 30-second version out loud without looking.
