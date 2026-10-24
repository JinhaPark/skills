# Valuation and investment policy

## Primary intrinsic valuation

Use Damodaran operating DCF and mandatory equity distress adjustment as the primary value judgment. FCF/CDS comparison selects candidates; multiples and reverse DCF only cross-check intrinsic value. Do not replace distress adjustment with a generic risk paragraph or an arbitrary fixed-cash sensitivity.

Derive segment revenue and normal margins from business drivers, after-tax operating profit, working capital and growth reinvestment to forecast annual FCFF. Connect growth, reinvestment and ROIC. Do not raise growth without its required investment. Explain competitive advantage and the period needed to converge to stable economics beyond the minimum three-year forecast table. If FCFE fits better, explain why and pair it with cost of equity; never mix FCFF and equity discounting.

Discount explicit FCFF and terminal value consistently. Construct WACC from sourced risk-free rate, risk premium, beta, debt cost, normal tax rate and market-value capital structure; distinguish observations from judgments. Match currency, nominal/real basis, taxes and cash-flow timing. Make terminal growth, margin, ROIC, reinvestment and cost of capital mutually consistent and disclose terminal-value share.

Bridge operating value to E_going using nonoperating assets, genuinely excess cash, debt, noncontrolling interests, priority claims and dilution. Do not classify all cash as excess. Avoid double counting leases, pensions, restructuring, SBC/dilution and acquisition-intangible amortization across cash flows and the value bridge.

## Mandatory distress comparison

Compare base DCF with E_adjusted = (1-p)*E_going + p*E_distress on every selected-company report. Define distress and p's horizon, source, estimation basis and probability measure. E_distress is present equity recovery after creditors and other priority claims; asset or debt recovery is not common-equity recovery. Align valuation date, currency, horizon and discount/probability convention.

For actual CDS verify reference entity, tenor, currency, seniority, restructuring terms, observation time, quote type/liquidity and debt-recovery assumptions. Risk-neutral Q is not physical P. Explain which probability is combined with which cash flow/discount convention. A single quote does not determine the entire hazard term structure or P. Alternative rating default cohorts or bond spreads need explicit horizon/population/liquidity limitations and must never be labeled actual CDS.

Do not invent p or equity recovery, substitute missing values with zero, or omit the comparison row. Preserve verified inputs; mark unavailable inputs and dependent adjusted value, per-share value and price margins NA with exact reasons. Continue feasible base DCF. Show hypothetical distress sensitivities separately from estimated probabilities, adjusted fair value and expected returns. Do not reuse an arbitrary fixed probability every week or count credit risk in WACC, hazard and mixture repeatedly.

Only when supported by term data, consider S(t)=exp(-integral(lambda(u)du)) as a separate survival-weighted extension. Do not automatically layer it onto the equity mixture. Use deterministic summation/integration when sufficient; Monte Carlo needs supported joint cash-flow/hazard variation. Never claim unexecuted extensions.

## Calculation dependency

Read JinhaPark/skills/distress-adjusted-dcf/SKILL.md, code and tests at the repository commit pinned by the parent. From that repository root actually execute:
`python -m unittest discover -s distress-adjusted-dcf/tests -v`

Calculate using the same tested commit. Record input values, units, sources, dates, SHA, command, actual outputs and independent formula checks. Local success is not observed remote CI success. Code-test success does not certify business forecasts. Disclose missing execution/failing tests and never claim completion falsely. Do not modify the dependency without separate authorization.

Respect dependency input validation: missing values, nonfinite numbers, type/domain errors or arithmetic-range failures become unavailable states with reasons, never zero, ranking inputs or price margins. Distinguish a validated actual zero from missing data.

One mandatory table includes going-concern enterprise/equity/per-share value, adjusted equity/per-share value, each per-share comparison with current price, p horizon/basis/measure, equity distress recovery, key assumptions and sensitivities. Keep NA rows. Separate verified estimates, business scenarios and hypothetical sensitivities.

## Cross-check and judgment

Compare suitable economic peers using appropriate P/E, EV/EBIT, EV/EBITDA or FCF yield while explaining growth, margin, capital intensity, accounting and mix differences. Never copy a famous company's multiple. Reverse the current price into conditional revenue, normal margin, reinvestment and FCF paths; it is not observed market consensus. Base/up/down cases vary business drivers and remain distinct from rate, terminal-growth and distress sensitivities.

State buy/watch/avoid judgment, conviction and limits for an actual selected report. Explain why this industry/company/price/time, what expectation differs, identifiable catalysts/events/metrics/time windows, and numerical thesis-breaking conditions. A good company may still be expensive. If all eligible candidates lack absolute value appeal, return no_selection to the coordinator instead of forcing a recommendation.

Date intrinsic ranges and future targets. Bridge future targets to future cash, debt and diluted shares. Do not attach arbitrary scenario probabilities to manufacture an average target. Conditional total returns specify holding period, price change and assumed cash dividends separately; disclose annualization, FX, dividend reinvestment and pretax assumptions. Do not count buyback benefits twice through both share/EPS assumptions and added returns. Current intrinsic-value margin is not a future return guarantee.

Check maturities, liquidity, interest coverage, ratings/outlooks and credit risk against appropriate peers. Compare actual CDS only on comparable terms and dates; preserve NA. Distinguish cash deterioration from default. Do not derive an investment decision from invented default probabilities.
