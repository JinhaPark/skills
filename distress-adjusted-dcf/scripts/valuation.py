from math import exp
from validation import finite_number, finite_series


def damodaran(going, distressed, probability):
    going = finite_number(going, 'going')
    distressed = finite_number(distressed, 'distressed')
    probability = finite_number(probability, 'probability')
    if not 0 <= probability <= 1 or distressed < 0:
        raise ValueError('invalid probability or recovery')
    try:
        result = (1-probability)*going + probability*distressed
    except OverflowError as exc:
        raise ValueError('equity valuation overflow') from exc
    return finite_number(result, 'equity valuation result')


def cds_hazard_approx(spread_bps, debt_recovery):
    spread_bps = finite_number(spread_bps, 'spread_bps')
    debt_recovery = finite_number(debt_recovery, 'debt_recovery')
    if spread_bps < 0 or not 0 <= debt_recovery < 1:
        raise ValueError('invalid CDS parameters')
    try:
        result = spread_bps/10000/(1-debt_recovery)
    except OverflowError as exc:
        raise ValueError('CDS hazard overflow') from exc
    return finite_number(result, 'CDS hazard result')


def survival(hazards, durations):
    hazards = finite_series(hazards, 'hazards')
    durations = finite_series(durations, 'durations')
    if not hazards or len(hazards) != len(durations):
        raise ValueError('unequal or empty periods')
    if any(h < 0 for h in hazards) or any(dt <= 0 for dt in durations):
        raise ValueError('invalid hazard/period')
    total = 0
    result = []
    for hazard, dt in zip(hazards, durations):
        try:
            total += hazard*dt
        except OverflowError as exc:
            raise ValueError('cumulative hazard overflow') from exc
        finite_number(total, 'cumulative hazard')
        result.append(finite_number(exp(-total), 'survival result'))
    return result
