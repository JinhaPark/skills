from valuation import survival
from validation import finite_number, finite_series


def enterprise_dcf(fcff, rates, hazards, durations, terminal, recovery):
    fcff = finite_series(fcff, 'fcff')
    rates = finite_series(rates, 'rates')
    hazards = finite_series(hazards, 'hazards')
    durations = finite_series(durations, 'durations')
    terminal = finite_number(terminal, 'terminal')
    recovery = finite_series(recovery, 'recovery')
    n = len(fcff)
    if not n or any(len(a) != n for a in (rates, hazards, durations, recovery)):
        raise ValueError('array mismatch or empty periods')
    if any(r <= -1 for r in rates) or any(rec < 0 for rec in recovery):
        raise ValueError('invalid rate or recovery')
    ss = survival(hazards, durations)
    prev = 1.0
    df = 1.0
    total = 0.0
    try:
        for f, r, dt, s, rec in zip(fcff, rates, durations, ss, recovery):
            divisor = finite_number((1+r)**dt, 'discount divisor')
            if divisor <= 0:
                raise ValueError('discount divisor underflow')
            df = finite_number(df/divisor, 'discount factor')
            if df == 0:
                raise ValueError('discount factor underflow')
            cashflow = finite_number(s*f+(prev-s)*rec, 'weighted cashflow')
            total = finite_number(total+df*cashflow, 'present value sum')
            prev = s
        return finite_number(total+df*ss[-1]*terminal, 'enterprise valuation result')
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError('enterprise valuation outside the supported numeric range') from exc
