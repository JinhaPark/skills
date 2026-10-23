---
name: distress-adjusted-dcf
description: Calculate Damodaran distress-adjusted DCF with CDS-based risk checks and numerical regression tests.
---

# Distress-adjusted DCF

Use `scripts/valuation.py` for Damodaran's equity mixture (1-p)*going-concern equity + p*distress equity. Equity recovery must be after priority claims. The optional period survival-weighted enterprise DCF is a separate extension and must not be confused with the equity mixture.

CDS-implied hazard ≈ spread/(1-debt recovery) is risk-neutral Q, not physical default probability P. A single CDS quote does not determine a whole term structure. Do not mix P/Q or count the same credit risk in both WACC and hazard without justification. Verify reference entity, tenor, liquidity, currency, seniority, date, recovery assumption and valuation inputs. Do not create unknown numbers. If data unavailable, report NA instead of a fabricated adjusted valuation.

Keep the report's four original cover-letter paragraphs and insert a subsection in deep research comparing base going-concern DCF, adjusted equity/share, default horizon and probability basis, distressed recovery, valuation sensitivity and current-price margin. Preserve source links and explicitly distinguish verified facts, scenarios and model limitations.

## Input and failure handling

Pass finite real numbers (Python `numbers.Real`, excluding `bool`); do not pass numeric strings, `None`, complex numbers, NaN or positive/negative infinity. Pass period arrays as sequences such as lists or tuples, with equal nonzero lengths. Invalid types raise `TypeError`; non-finite values, invalid domains and unsupported arithmetic ranges raise `ValueError`. Validate all inputs even when their weight is zero.

Allow negative FCFF, going-concern equity and terminal value. Preserve the model domains: distressed/recovery amounts and hazards/spreads are nonnegative; probability is in [0, 1]; debt recovery is in [0, 1); durations are positive; discount rates exceed -1. Outputs and cumulative hazards must remain finite; reject discount divisor/factor overflow or underflow. Finite cumulative hazards may produce survival 0 through exponential underflow; explicit valid zero inputs/results remain valid.

At the caller, check required data before calculation. On missing data or `TypeError`/`ValueError`, return an unavailable state (for example `status: unavailable`, `value: null`, and a reason naming the missing/invalid field). Display “NA — 자료 부족/입력 오류/계산 범위 초과” as applicable. Never substitute 0 for absent values, catch an error and return 0, or include unavailable results in price margins/rankings. Report a genuine computed zero only with validated complete inputs and stated assumptions. Do not silently drop periods or coerce strings into numbers.

## Verification

From the repository root run `python -m unittest discover -s distress-adjusted-dcf/tests -v` before reporting numerical outputs. The same command runs in GitHub Actions on pull requests and pushes to main (Python 3.11–3.13). Distinguish a local pass from an observed remote CI pass.

Sources: https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/distresspaper.htm ; https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/a21.htm
