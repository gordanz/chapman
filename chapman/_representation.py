import numpy as np
np.set_printoptions(suppress=True, precision=3)


def info(m):
    out_title = f"Basic info for: \"{m.title}\"\n"
    out_underl = "-"*(len(out_title)-1)+"\n"
    transitions = " , ".join(
            [ "("+s1 + " -> "+ s2+ ", "
                    +str(np.float32(dct["weight"]))+")" for
            s1, s2, dct in m.transitions(data=True) ]
            )

    out = out_title + out_underl + \
    f"""\n - states ({m.number_of_states()}): {m.states}
 
 - transitions ({m.number_of_transitions()}): {transitions}
"""
    return(out)

def info_classes(m):
    assert m._classes_computed, "Compute classes first."

    out_title = f"Class info for: \"{m.title}\"\n"
    out_title += "-"*(len(out_title)-1)+"\n"
    if m.is_aperiodic:
        period_info = f"""\n - the chain is aperiodic (all states have period 1).\n"""
    else:
        period_info = f"""\n - the chain is not aperiodic. States with nontrivial periods: """
        dict_period = { state: m.states[state]["period"] \
                for state in m.states \
                if m.states[state]["period"]>1 }
        period_info += dict_period.__repr__() + "\n"

    if m.is_irreducible:
        reduc_info = "\n - the chain is irreducible (single, recurrent class).\n\n"
    else:
        reduc_info = f"\n - the chain is not irreducible. It has {m.number_of_classes} classes. \n"

    out_classes = out_title + period_info 
    out_classes += reduc_info


    out_classes +=f"""\n - classes ({m.number_of_classes}): {m.classes}

 - transient classes ({m.number_of_transient_classes}, T = {m.number_of_transient_states}): {m.transient_classes}

 - recurrent classes ({m.number_of_recurrent_classes}, C = {m.number_of_recurrent_states}): {m.recurrent_classes}
"""
    return(out_classes)

def info_stationary(m):
    assert m._classes_computed , "Compute first."
    out_title = f"Stationary distributions for: \"{m.title}\"\n"
    out = out_title+"-"*(len(out_title)-1)+"\n"
    for i,aclass in enumerate(m.recurrent_classes):
        out += f"\nRecurrent Class {i+1}\n"
        for s in sorted(aclass):
            sprob = m.states[s]["stationary"] 
            out += f"{s}: {sprob:.3f}\n"
    return(out)

def info_P(m):
    assert m._P_matrix_computed, "Compute the matrix P first."
    out_title = f"P-matrix info for: \"{m.title}\"\n"
    out_title += "-"*(len(out_title)-1)+"\n"
    out = out_title+f""" - transition matrix: 
{m.P}
"""
    out += "\n - order of states:"+ m.I_to_S.__repr__()+"\n"
    return(out)

def info_QRF(m):
    out_title = f"QRF info for: \"{m.title}\"\n"
    out_title += "-"*(len(out_title)-1)+"\n"
    if m.no_transient: out = "\n - no transient states. Q, R and F are not defined."
    else:
        assert m._QRF_matrix_computed, "Compute QRF first."
        out= f"""\n - matrix Q (T x T): 
   {m.Q}

 - matrix R (T x C): 
   {m.R}

 - fundamental matrix F=(I-Q)^{-1} (T x T): 
   {m.F}
"""

        out += "\n - order of T-states: "+ m.T_to_S.__repr__()+"\n"
        out += "\n - order of C-states: "+ m.C_to_S.__repr__()
    return(out_title+out)
  
