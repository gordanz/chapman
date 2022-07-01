import numpy as np

def _draw_next_index(m,i):
    assert m._P_matrix_computed, "Compute P first"
    probs = m.P[i]
    return(np.random.choice(len(probs),p = probs))

def simulate(m, s, nsim = 10):
    """Returns a simulated trajectory from chain m of 
    size nsim+1, which starts with the state s

    Args:
        m (MarkovChain): the chain from which to simulate
        s (str): the initial state
        nsim (int): number of steps (default = 10)

    Returns:
        list: a list of states
    """
    assert m._P_matrix_computed, "Compute P first"
    i = m.S_to_I[s]
    out = [s]
    for j in range(nsim):
        i_next = _draw_next_index(m,i);
        i = i_next
        out.append( m.I_to_S[i] )
    return(out)

