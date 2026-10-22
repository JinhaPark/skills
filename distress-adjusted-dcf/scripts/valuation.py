from math import exp

def damodaran(going, distressed, probability):
    if not 0 <= probability <= 1 or distressed < 0:
        raise ValueError('invalid probability or recovery')
    return (1-probability)*going + probability*distressed

def cds_hazard_approx(spread_bps, debt_recovery):
    if spread_bps < 0 or not 0 <= debt_recovery < 1:
        raise ValueError('invalid CDS parameters')
    return spread_bps/10000/(1-debt_recovery)

def survival(hazards, durations):
    if not hazards or len(hazards)!=len(durations):
        raise ValueError('unequal periods')
    total=0
    result=[]
    for hazard, dt in zip(hazards,durations):
        if hazard<0 or dt<=0: raise ValueError('invalid hazard/period')
        total += hazard*dt
        result.append(exp(-total))
    return result
