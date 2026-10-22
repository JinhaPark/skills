---
name: distress-adjusted-dcf
description: Calculate Damodaran distress-adjusted DCF with CDS-based risk checks and numerical regression tests.
---

# Distress-adjusted DCF

Use `scripts/valuation.py` for Damodaran's equity mixture (1-p)*going-concern equity + p*distress equity. Equity recovery must be after priority claims. The optional period survival-weighted enterprise DCF is a separate extension and must not be confused with the equity mixture.

CDS-implied hazard ≈ spread/(1-debt recovery) is risk-neutral Q, not physical default probability P. A single CDS quote does not determine a whole term structure. Do not mix P/Q or count the same credit risk in both WACC and hazard without justification. Verify reference entity, tenor, liquidity, currency, seniority, date, recovery assumption and valuation inputs. Do not create unknown numbers. If data unavailable, report NA instead of a fabricated adjusted valuation.

Keep the report's four original cover-letter paragraphs and insert a subsection in deep research comparing base going-concern DCF, adjusted equity/share, default horizon and probability basis, distressed recovery, valuation sensitivity and current-price margin. Preserve source links and explicitly distinguish verified facts, scenarios and model limitations.

Run `python -m unittest discover -s tests -v` before reporting numerical outputs.

Sources: https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/distresspaper.htm ; https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valquestions/a21.htm
