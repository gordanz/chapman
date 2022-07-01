import networkx as nx
import numpy as np
from fractions import gcd
EPS = 0.0001  # used to check for stochasticity

def _compute_P_matrix(m):
    m._P_matrix_computed = True
    
    # compute dictionaries 
    m.I_to_S = { i:s for i,s in enumerate(m.states) }
    m.S_to_I = { s:i for i,s in enumerate(m.states) }
    
    # the transition matrix
    m.P = np.array(nx.adjacency_matrix(m).todense())
    
    # check to see if it is stochastic
    ones = np.ones([m.number_of_states(), 1])
    deviation = np.linalg.norm(ones - m.P @ ones)
    assert deviation < EPS, \
        "Transition matrix is not stochastic. " + \
        "Deviation = "+str(deviation)+"\n "+str(m.P)

def _compute_period(m, state, class_of_state):
    levels = {state: 0}
    this_level = [state]
    G = m
    g = 0
    l = 1
    while this_level:
        next_level = []
        for u in this_level:
            for v in [ v for v in G[u] if v in class_of_state ]:
                if v in levels:  # Non-Tree Edge
                    g = gcd(g, levels[u] - levels[v] + 1)
                else:  # Tree Edge
                    next_level.append(v)
                    levels[v] = l
        this_level = next_level
        l += 1
    # period 0 is period 1
    if g == 0:
        g = 1 
    return(g)

def _normalize(l):
    return(l/sum(l))

def _compute_classes(m):

    # to check that it is a valid chain 
    if not m._P_matrix_computed:
        _compute_P_matrix(m)

    m._classes_computed = True
    
    # classes
    components = nx.strongly_connected_components(m)
    condensation_edges = nx.condensation(m).edges
    m.classes = [ [s for s in component] for component in components]
    m.number_of_classes = len(m.classes)
    assert m.number_of_classes > 0, \
        "Zero classes - something wrong"
    m.is_irreducible = m.number_of_classes == 1
    
    # recurrent and transient class component_indices
    m.transient_class_indices = \
            sorted(np.unique(
                [comp1 for (comp1, comp2) in condensation_edges ]))
    m.number_of_transient_classes = len(m.transient_class_indices)
    m.number_of_recurrent_classes = \
            m.number_of_classes - m.number_of_transient_classes 
    m.no_transient = m.number_of_transient_classes == 0
   
    m.number_of_transient_states = 0
    m.number_of_recurrent_states = 0
    for c in range(m.number_of_classes):
        if c in m.transient_class_indices:
            for s in m.classes[c]:
                m.states[s]["type"] = "T"
                m.states[s]["class"] = c
                m.number_of_transient_states += 1
        else:
            for s in m.classes[c]:
                m.states[s]["type"] = "R"
                m.states[s]["class"] =c
                m.number_of_recurrent_states += 1
    
    transient_index = 0
    recurrent_index = 0
    for j,s in enumerate(m.states):
        m.states[s]["index"] = j
        if m.is_transient(s):
            m.states[s]["transient_index"] = transient_index
            transient_index += 1
        else:
            m.states[s]["recurrent_index"] = recurrent_index
            recurrent_index += 1
   
    m.transient_states = \
        [ s for s in m.states if m.is_transient(s) ]
    
    m.transient_state_indices = \
        [ m.S_to_I[s] for s in m.states if m.is_transient(s) ]
    
    m.recurrent_states = \
        [ s for s in m.states if m.is_recurrent(s) ]
    
    m.recurrent_state_indices = \
        [ m.S_to_I[s] for s in m.states if m.is_recurrent(s) ]

    m.transient_classes = [m.classes[i] for i in m.transient_class_indices]
    m.recurrent_classes = [m.classes[i] for i in range(m.number_of_classes)\
            if i not in m.transient_class_indices]

    # computing stationary distributions
    for aclass in m.recurrent_classes:
        class_indices = [m.S_to_I[s] for s in aclass]
        PC = m.P[class_indices][:,class_indices]
        I = np.identity(PC.shape[0])
        u,s,vh  = np.linalg.svd(PC-I)
        pi = list(_normalize(np.transpose(u)[-1]))
        for i,s in enumerate(aclass):
            m.states[s]["stationary"] = pi[i]

    m.T_to_S = \
            { i:m.I_to_S[m.transient_state_indices[i]] for
                    i in range(m.number_of_transient_states)}
    m.C_to_S = \
            { i:m.I_to_S[m.recurrent_state_indices[i]] for
                    i in range(m.number_of_recurrent_states)}
    m.S_to_T = \
            { v:k for k,v in m.T_to_S.items()}

    m.S_to_C = \
            { v:k for k,v in m.C_to_S.items()}

    # computing periods of states
    
    m.is_aperiodic = True
    for aclass in m.classes:
        s = aclass[0]
        per = _compute_period(m,s,aclass)
        if per > 1:
            m.is_aperiodic = False
        for state in aclass:
            m.states[state]["period"] = per

def _compute_QRF_matrices(m):
    assert m._classes_computed, \
            "Compute first."
    assert not m.no_transient, \
            "Cannot compute QRF for a recurrent chain."
   
    m._QRF_matrix_computed = True
    
    # canonical decomposition of P
    # Q-matrix
    m.Q = m.P[m.transient_state_indices][:, m.transient_state_indices]

    # R-matrix
    m.R = m.P[m.transient_state_indices][:, m.recurrent_state_indices]

    # F-matrix
    I = np.identity(m.Q.shape[0])
    m.F = np.linalg.inv(I-m.Q)

def _recurrent_chains(m):
    n = m.number_of_classes;
    recurrent_classes = [ m.classes[i] for i in range(m.number_of_classes)\
            if i not in m.transient_class_indices ]
    subgraphs = []
    for i,aclass in enumerate(recurrent_classes):
        mc = m.subgraph(aclass).copy()
        mc.title = "Recurrent_class_C"+str(i+1)
        mc.compute()
        subgraphs.append(mc)
    return(subgraphs)

def _stationary_of_class(m, sz):
    assert m._classes_computed, "Compute Classes First"
    d = {}
    for s in m.states():
        if m.states[s]["class"]==m.states[sz]["class"]:
            d[s] = m.states[s]["stationary"]
    return(d)




    

