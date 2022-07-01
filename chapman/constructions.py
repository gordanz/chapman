import chapman as mk
import numpy as np


def _pair_name(s1,s2):
    return( f"({s1},{s2})" )

def product(m1, m2):
    """Builds the product chain from two Markov chains

    Args:
        m1, m2 (MarkovChain):

    Returns:
        m (Markov Chain)
    """

    m = mk.MarkovChain(
            title = f"Product of \'{m1.title}\' and \'{m2.title}\'")
    prod = [ (s1,s2) for s1 in m1.states() for s2 in m2.states() ]
    states = [ _pair_name(s1,s2) for s1,s2 in prod ]

    for s in states:
        m.add_state(s)

    for s1A, s2A in prod:
        for s1B, s2B in prod:
            if m1.has_edge(s1A, s1B) and m2.has_edge(s2A, s2B):
                p1 = m1[s1A][s1B]['weight']
                p2 = m2[s2A][s2B]['weight']
                m.add_transition( _pair_name(s1A, s2A), 
                        _pair_name(s1B, s2B),
                        probability = p1*p2)
    m.compute()
    return(m)
            

