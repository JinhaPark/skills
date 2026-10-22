from valuation import survival

def enterprise_dcf(fcff, rates, hazards, durations, terminal, recovery):
    n=len(fcff)
    if not n or any(len(a)!=n for a in (rates,hazards,durations,recovery)):
        raise ValueError('array mismatch')
    ss=survival(hazards,durations)
    prev=1.0
    df=1.0
    total=0.0
    for f,r,dt,s,rec in zip(fcff,rates,durations,ss,recovery):
        if r<=-1 or rec<0: raise ValueError('invalid inputs')
        df /= (1+r)**dt
        total += df*(s*f+(prev-s)*rec)
        prev=s
    return total+df*ss[-1]*terminal
