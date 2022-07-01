import math
import sys, inspect
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout 
from chapman.base import MarkovChain


def _good_function(mod, func_name, func):
    return (  inspect.isfunction(func) and inspect.getmodule(func) == mod and
not func_name[0] == '_' and not func_name == "list_examples" )

def list_examples():
    """Prints out the names of all  currently implemented examples."""

    this_module = sys.modules[__name__] 
    dct = inspect.getmembers(this_module)
    good = [ k for k,v in dct if _good_function(this_module,k,v) ]
    print(sorted(good))

def _rst(alpha, sx, sy, dx, dy, x,y):
    """Helper for rotate_scale_translate"""

    PI_OVER_180 = 0.0174533
    cosa = math.cos(alpha*PI_OVER_180)
    sina = math.sin(alpha*PI_OVER_180)
    xp = sx*(cosa * x + sina * y)+dx
    yp = sy*(sina * x - cosa * y)+dy
    return([xp,yp])

def _rotate_scale_translate(point_dict, angle = 0, stretch_x = 1, 
        stretch_y = 1,  move_x = 0, move_y = 0):
    """Applies an affine transformation to a layout dictionary 
    for a Markov chain

    args:
        point_dict (dict): dictionary of states to positions [x,y]
        angle (float, optional) : angle of rotation
        stretch_x(float, optional) : stretch factor in x, defaults to 1
        stretch_y(float, optional) : stretch factor in y, defaults to 1
        move_x(float, optional) : translation in x, defaults to 1
        move_y(float, optional) : translation in y, defaults to 0

    Returns:
        a layout dictionary (dict of positions [x,y,z,...] with z, ...
        discarded)

    """
    return( { k:_rst(angle, stretch_x, stretch_y, move_x, move_y, v[0], v[1]) 
        for k,v in point_dict.items()} )

def _curve_doubles(m, curve = 0.15):
    """If there are edged going both ways between two states, curve
    them.
    
    Args:
        m (MarkovChain): the chain
        curve (float): the amount of curvature (default = 0.15)
    """
    for s1 in m.states():
        for s2 in m.states():
            if m.has_edge(s1,s2) and m.has_edge(s2,s1):
                m.set_curve(s1,s2,curve)
                m.set_curve(s2,s1,curve)

def random_walk( T = 4, p=0.5, reflecting = False):
    """ Random walk as a Markov chain. T is the time horizon, p is the
    probability of ''up''. States are {-T,-T-1,..., T-1, T}.
    If reflecting is True, both boundaries T and -T are reflective,
    otherwise they are absorbing.

    Args:
        T (int): time horizon (default 4)
        p (float): the probability of an up-step (default 0.5)
        reflecting (bool): boundary behavior

    Returns:
        a MarkoChain object
    """
    assert T > 0 and p>0 and p<1, "Must have T>0, p in (0,1)"
    q = 1-p
    m = MarkovChain(title = f"Random_walk")
    for i in range(-T,T+1):
        m.add_state(str(i), position = [i,0])
    for i in range(-T+1,T):
        m.add_transition(str(i), str(i+1), probability = p, label = "p",
                curve = 0.15)
        m.add_transition(str(i), str(i-1), probability = q, label = "q",
                curve = 0.15)
    if reflecting:
        m.add_transition(str(T),str(T-1), probability = 1, curve = 0.15)
        m.add_transition(str(-T),str(-T+1), probability = 1, curve = 0.15)
    else:
        m.add_transition(str(T),str(T))
        m.add_transition(str(-T),str(-T))
        m.set_loop_direction(str(T), "u")
        m.set_loop_direction(str(-T), "u")

    m.set_canvas(70*T,50)
    m.compute()
    return(m)


def attached_cycles(n1 = 4, n2 = 6, pA = 0.5, tail = False):
    """A Markov chain with two attached cycles and a tail.

    Args:
        n1 (int) : size of the first cycle
        n2 (int) : size of the second cycle
        pA (float) : probability of choosing the first cycle
        tail (bool) : whether to add a tail to the chain

    Returns: 
        a MarkovChain object

    """
    assert n1 > 1 and n2 > 1, \
            "Cycles need to be at least 2 states in length"
    
    m=MarkovChain(title="Attached_Cycles")

    # nodes (must make them explicitly blue if you use graphviz)
    m.add_state("AB1")

    for i in range(2,n1+1):
        m.add_state("A"+str(i))
    
    for i in range(2,n2+1):
        m.add_state("B"+str(i))

    m.add_transition("AB1","A2", probability = pA)
    m.add_transition("AB1","B2", probability = pA)
    m.add_transition("A"+str(n1),"AB1")
    m.add_transition("B"+str(n2),"AB1")
    if n1 > 2:
        for i in range(2,n1):
            m.add_transition("A"+str(i), "A"+str(i+1))
    if n2 > 2:
        for i in range(2,n2):
            m.add_transition("B"+str(i), "B"+str(i+1))

    # adding a tail
    if tail:
        m.add_state("C2")
        m.add_transition("AB1","C2")
        m.add_transition("C2","C2")
        m.set_probability("AB1","A2",pA/2)
        m.set_probability("AB1","C2",pA/2)

    # Layout
    ###############
    # pre_layout = graphviz_layout(m.graph, prog="fdp", 
            # args = "-Gmodel=subset -Gnodesep=1.5") 
    pre_layout = nx.kamada_kawai_layout(m, weight=1)
    layout = _rotate_scale_translate(pre_layout, angle = -90, 
            stretch_x = 2, stretch_y = 2)
    for s,pos in layout.items():
        m.states[s]["position"]= pos
    m.set_canvas(180,150)
    m.compute()
    return(m)

def gambler(a=5, p=0.25):
    """The chain for "Gambler's ruin" problem.

    Args: 
        p (float): the probability of winning in a single round
        a (int): the goal amount

    Returns: 
        a MarkovChain object.
    """
    
    assert a>2, "a must be at least 3"
    assert 0<p and p<1, "p must be in (0,1)"

    m=MarkovChain(title="Gambler")

    # nodes (must make them explicitly blue if you use graphviz)
    for i in range(a+1):
        m.add_state(str(i), color="blue", position = [i,0]);
        
    m.set_color(str(0),"orange")
    m.set_color(str(a),"orange")

    # transitions
    for i in range(1,a):
        m.add_transition(str(i), str(i-1), 
                probability = 1-p,
                label = "1-p",curve = 0.2)
        m.add_transition(str(i), str(i+1), 
                probability = p,
                label = "p", curve = 0.2)
    m.set_curve(str(1), str(0),0)
    m.set_curve(str(a-1), str(a),0)

    m.add_transition(str(0), str(0))
    m.add_transition(str(a), str(a))
    m.set_loop_direction(str(0),"u")
    m.set_loop_direction(str(a),"u")

    # Layout
    ###############

    m.set_canvas(180,150)
    m.compute()
    return(m)


# def mc8_1():
    # # """The chain for problem MC8_1 
    
    # # Returns: a MarkovChain object
    # # """
    
    # m=MarkovChain(title="MC8_1")

    # # nodes (must make them explicitly blue if you use graphviz)
    # for i in range(8):
        # m.add_state(str(i+1), color="blue");

    # # From 1
    # m.add_transition("1","1",probability = 0.5, label="1/2")
    # m.add_transition("1","2",probability = 0.5, label="1/2")

    # # From 2
    # m.add_transition("2","3",probability = 0.5, label="1/2")
    # m.add_transition("2","7",probability = 0.5, label="1/2")

    # # From 3
    # m.add_transition("3","4",curve = 0.2)

    # # From 4
    # m.add_transition("4","3",probability = 0.5, label="1/2",curve=0.2);
    # m.add_transition("4","5",probability = 0.5, label="1/2")

    # # From 5
    # m.add_transition("5","6")

    # # From 6
    # m.add_transition("6","3",probability = 0.5, label="1/2")
    # m.add_transition("6","6",probability = 0.5, label="1/2")

    # # From 7
    # m.add_transition("7","8",curve=0.2);

    # # From 5
    # m.add_transition("8","7",probability = 0.75, label="3/4", curve=0.2);
    # m.add_transition("8","8",probability = 0.25, label="1/4")

    # # loops
    # m.set_loop_direction("1","ur")
    # m.set_loop_direction("8","ur")
    # m.set_loop_direction("6","ur")

    # # Layout
    # ###############
    # pre_layout = graphviz_layout(m, prog="fdp", 
            # args = "-Gmodel=subset -Gnodesep=1.5") 
    # layout = _rotate_scale_translate(pre_layout, angle = -90, 
            # stretch_x = 2, stretch_y = 2)
    # m.set_layout(layout)
    # m.set_canvas(180,150)
    # m.compute()
    # return(m)

# def facility(p=0.4):
    # """The chain for problem about the airline reservation system and its
    # computers which get repaired
    
    # Args: 
        # p (float): the probability of a computer breakdown

    # Returns: 
        # a MarkovChain object
    # """

    # m = MarkovChain(title = "MC14-1")

    # # states
    # m.add_state("0-0-1-1", shape = 1);
    # m.add_state("2-0-0-0", shape = 1);
    # m.add_state("1-1-0-0", shape = 1);
    # m.add_state("0-1-0-1", shape = 1);
    # m.add_state("1-0-1-0", shape = 1);
    
    # # edges
    # m.add_transition("0-0-1-1","0-1-0-1",
            # label="1", probability = 1)
    # m.add_transition("2-0-0-0","0-0-1-1",
            # label="p^2", probability = p**2 )
    # m.add_transition("2-0-0-0","2-0-0-0",
            # label="(1-p)^2", probability = (1-p)**2)
    # m.add_transition("2-0-0-0","1-0-1-0",
            # label="2p(1-p)", probability = 2* p*(1-p) )
    # m.add_transition("1-1-0-0","2-0-0-0",
            # label="1-p", probability = (1-p) )
    # m.add_transition("1-1-0-0","1-0-1-0",
            # label="p",curve=0.2, probability = p)
    # m.add_transition("1-0-1-0","1-1-0-0",
            # label="1-p",curve=0.2, probability = (1-p) )
    # m.add_transition("1-0-1-0","0-1-0-1",
            # label="p",curve=0.2, probability = p )
    # m.add_transition("0-1-0-1","1-0-1-0",
            # label="1",curve=0.2, probability = 1 )
    
    # # loops
    # m.set_loop_direction("2-0-0-0","d")
    
    # # Layout
    # pre_layout =  nx.kamada_kawai_layout(m, weight = 1)
    # layout = _rotate_scale_translate(pre_layout, angle = -80)
    # m.set_layout(layout)
    # m.compute()
    # return(m)

# def mc20_1():
    # # """The chain for problem MC20_1."""
    
    # m = MarkovChain(title="MC20_1")
    # g = m

    # m.set_canvas(140,130)

    # # nodes
    # for i in range(7):
        # m.add_state(str(i))

    # the_transitions = {
            # (1,2,1,"1"),
            # (2,3,1,"1"),
            # (3,4,1,"1"),
            # (4,5,1,"1"),
            # (5,1,1,"1"),
            # (0,1,0.5,"1/2"),
            # (0,6,0.5,"1/2"),
            # (6,6,1,"1")
            # }

    # for (i1,i2,p,l) in the_transitions:
        # m.add_transition(str(i1), str(i2), probability = p, label = l)

    # # pre_layout =  nx.kamada_kawai_layout(g, weight = 1)
    # pre_layout = graphviz_layout(g, prog="neato", args = "-Gnodesep=1.5") 
    # layout = _rotate_scale_translate(pre_layout, angle = -90, stretch_x = 20, 
            # stretch_y = 20)
    # m.set_layout(layout)
    # # m.compute()
    # return(m)


# def mc21_1():
    # # """The chain for problem MC21_1
    
    # # Returns: a MarkovChain object
    # # """

    # m = Markov(title="MC21_1")
    # g = m
   
    # # states
    # for state in range(1,3+1):
        # m.add_state(str(state))
   
    # # transitions
    # m.add_transition( "1","2", probability = 1, label = "1", curve = 0.1)
    # m.add_transition( "2","1", probability = 0.25, label = "1/4", curve = 0.1)
    # m.add_transition( "2","2", probability = 0.50, label = "1/2")
    # m.add_transition( "2","3", probability = 0.25, label = "1/4")
    # m.add_transition( "3","3", probability = 1, label = "1", color="orange")
   
    # # loop directions
    # m.set_loop_direction("2","d")
    # m.set_loop_direction("3","d")
    
    # # the layout
    # pre_layout = graphviz_layout(g, prog="dot", args = "-GNodesep=1")
    # the_layout = _rotate_scale_translate(pre_layout, angle = 90)
    # m.set_layout(the_layout)
    # m.compute()
    # return(m)

def professor(p_morning = 0.05, p_afternoon = 0.20):
    """The Markov chain with the professor and umbrellas.

    Args:
        p_morning (float): probability of raining in the morning. Defaults
            to 0.05.
        p_afternoon (float): probability of raining in the afternoon.
            Defaults to 0.2.

    Returns: 
        a MarkovChain object

    """
    # constants
    q_morning = 1-p_morning
    q_afternoon = 1-p_afternoon
    p_morning_label = "p_m"
    q_morning_label = "q_m"
    p_afternoon_label = "p_a"
    q_afternoon_label = "q_a"
    
    
    m = MarkovChain(title = "professor")
    g = m
    
    for p in ["H", "O"]:
        for u in range(6):
            m.add_state( p+str(u))
    
    # absorbing states get a different color and a loop direction
    m.set_color("H5","orange")
    m.set_color("O5","orange")
    
    m.set_loop_direction("H5","d")
    m.set_loop_direction("O5","u")
    
    # add edges to g
    for i in range(5):
        init = "H" + str(i)
        term = "O" + str(4 - i)
        m.add_transition(init, term, 
                probability=q_morning, 
                label=q_morning_label, 
                curve = 0.2)
    
        if i>0:
            init = "H" + str(i)
            term = "O" + str(5 - i)
            m.add_transition(init, term, 
                    probability=p_morning, 
                    label=p_morning_label, 
                    curve = 0.2)
    
        init = "O" + str(i)
        term = "H" + str(4 - i)
        m.add_transition(init, term, 
                probability=q_afternoon, 
                label=q_afternoon_label, 
                curve = 0.2)
    
        if i>0:
            init = "O" + str(i)
            term = "H" + str(5 - i)
            m.add_transition(init, term, 
                    probability=p_afternoon, 
                    label=p_afternoon_label, 
                    curve = 0.2)
    
    m.add_transition("H0", "H5", 
            probability=p_morning, 
            label=p_morning_label)
    m.add_transition("O0", "O5", 
            probability=p_afternoon, 
            label=p_afternoon_label)
    m.add_transition("H5", "H5")
    m.add_transition("O5", "O5")
    
    # make arrow between O2 and H2 curve a bit more
    m.set_curve("O2","H2",0.5)
    m.set_curve("H2","O2",0.5)
    
    # Layout
    
    manual_layout = {
            'H5': [0.2,0], 'H0': [1,0], 'O4': [2,0], 
            'H1': [3,0], 'O3': [4,0], 'H2': [5,0],
            'O2': [5,1], 'H3': [4,1], 'O1': [3,1], 
            'H4': [2,1], 'O0': [1,1], 'O5': [0.2,1]
            }

    m.set_canvas(220,100)
    the_layout = _rotate_scale_translate(manual_layout, 
            stretch_x =  10, stretch_y = 10, 
            move_x = 20, move_y = 20)
    m.set_layout(the_layout)
    
    # last minute tweaks
    m.set_name("H5","Hw")
    m.set_name("O5","Ow")
    m.set_label("Hw","Hw")
    m.set_label("Ow","Ow")

    m.compute()
    return(m)

def tennis(p = 0.4):
    """The tennis chain.

    Args:
        p (float): the probability that S wins in a single rally

    Returns: 
        a MarkovChain object

    """
    m = MarkovChain(title = "tennis")
    g = m

    points = ["0","15","30","40","A"]
    
    def label(l):
        [i,j] = l
        if i<5 and j<5:
            return(""+points[i]+"-"+points[j]+"")
        elif i==5:
            return("$S_{win}$")
        else:
            return("$R_{win}$")
    
    def name(l):
        [i,j] = l
        if i<5 and j<5:
            return(""+points[i]+"-"+points[j]+"")
        elif i==5:
            return("S")
        else:
            return("R")
    
    
    # BUILDING THE GRAPH
    nodes_game = [ [i,j] for i in range(4) for j in range(4) ]
    nodes_other = [ [3,4], [4,3], [5,0], [0,5] ]
    nodes = nodes_game+nodes_other
    
    for nd in nodes:
        clr = "blue"
        if nd == [5,0] or nd == [0,5]:
            clr = "orange"
        m.add_state(name(nd),label=label(nd),color=clr)
   
    m.set_loop_direction(name([5,0]),"d")
    m.set_loop_direction(name([0,5]),"u")

    p_label = 'p'
    q_label = 'q'
    q=1-p
    
    for i in range(4):
        for j in range(4):
            if i<3:
                m.add_transition(name((i,j)), name((i+1,j)),
                        label=p_label, probability = p)
            elif j<3:
                m.add_transition(name((i,j)), name((5,0)),
                        label=p_label, probability = p)
            if j<3: 
                m.add_transition(name((i,j)), name((i,j+1)),
                        label=q_label, probability = q)
            elif i<3:
                m.add_transition(name((i,j)), name((0,5)),
                        label=q_label, probability = q)

    # advantages back and forth
    m.add_transition(name((3,3)),name((3,4)),
            label=q_label, curve=0.2, probability=q)
    m.add_transition(name((3,3)),name((4,3)),
            label=p_label, curve=0.2, probability=p)
    m.add_transition(name((4,3)),name((3,3)),
            label=q_label, curve=0.2, probability=q)
    m.add_transition(name((3,4)),name((3,3)),
            label=p_label, curve=0.2, probability=p)
    
    # wins
    m.add_transition(name((3,4)),name((0,5)),
            label=q_label,  probability=q)
    m.add_transition(name((4,3)),name((5,0)),
            label=p_label,  probability=p)
    m.add_transition(name((5,0)),name((5,0)))
    m.add_transition(name((0,5)),name((0,5)))
    
    
    # Layout
    m.set_canvas(160,110)
    pre_layout =  nx.kamada_kawai_layout(g, weight = 1)
    the_layout = _rotate_scale_translate(pre_layout, 
            angle = -104, stretch_x = 20, stretch_y = 20, 
            move_x = 30, move_y = 30)
    m.set_layout(the_layout)
    m.compute()
    return(m)


# def mc10_5_6():
    # """The chain used in problem 10.5.6"""

    # m = MarkovChain(title = "MC10_5_6")
    # states = [ str(i) for i in range(1,8) ]
    # for s in states:
        # m.add_state(s)

    # transitions = [
            # (1,2,0.5),
            # (1,3,0.5),
            # (2,1,1),
            # (3,1,0.5),
            # (3,2,0.5),
            # (4,3,0.25),
            # (4,5,0.5),
            # (4,6,0.25),
            # (5,6,1),
            # (6,6,0.5),
            # (6,7,0.5),
            # (7,6,1) ]


    # for i1,i2,p in transitions:
        # if p == 0.5:
            # lb = "1/2"
        # elif p == 0.25:
            # lb = "1/4"
        # else:
            # lb = str(p)

        # m.add_transition(str(i1), str(i2), probability = p, label = lb)

    # curves = [
            # (6,7),
            # (7,6), 
            # (1,3),
            # (3,1),
            # (1,2),
            # (2,1)]

    # for i1,i2 in curves:
        # m.set_curve(str(i1), str(i2), 0.15)

    # m.set_loop_direction("6","ul")
    # m.compute()

    # # Layout
    # ###############
    # m.set_canvas(180,120)
    # pre_layout = nx.kamada_kawai_layout(m, weight = 1)
    # layout = _rotate_scale_translate(pre_layout, angle = 20, 
             # stretch_x = 2, stretch_y = 2)
    # m.set_layout(layout)
    # return(m) 

# def mc10_5_3(p=0.4, a=6):
    # """The chain used in the problem 10.5.6
    
    # Args:
        # p (float): the probability that of a single win 
        # a (int): the amount required to exit

    # Returns: 
        # a MarkovChain object
    # """
    # m = MarkovChain(title = "MC10_5_3")
    # states = [ str(i) for i in range(a+1) ]
    # for s in states:
        # m.add_state(s)

    # m.add_transition("0","0")
    # m.add_transition(str(a),str(a))
    # m.set_loop_direction("0","u") 
    # m.set_loop_direction(str(a),"r") 
    # for i in range(1,a):
        # j = min( i, a-i)
        # m.add_transition(str(i),str(i-j),probability = 1-p, label = "q")
        # m.add_transition(str(i),str(i+j),probability = p, label = "p")

    # _curve_doubles(m)
    # m.compute()

    # # Layout
    # ###############
    # m.set_canvas(180,120)
    # pre_layout = graphviz_layout(m, prog="dot", args = "-GNodesep=0.1")
    # pre_layout = nx.shell_layout(m, [["2","4"],["0","1","3","5"]])
    # layout = _rotate_scale_translate(pre_layout, angle = 0, 
             # stretch_x = 2, stretch_y = 2)
    # m.set_layout(layout)
    # return(m) 

# def mc10_5_1():

    # m = MarkovChain(title = "MC10_5_1")
    # for i in range(1,8):
        # m.add_state(str(i))

    # trs = [
            # (1,1,0.5),
            # (1,3,0.5),
            # (2,1,0.25),
            # (2,2,0.5),
            # (2,3,0.25),
            # (3,2,0.5),
            # (3,3,0.5),
            # (4,3,1),
            # (5,4,0.5),
            # (5,6,0.5),
            # (6,7,1),
            # (7,6,0.5),
            # (7,7,0.5)
            # ]

    # for i1,i2,p in trs:
        # m.add_transition(str(i1), str(i2), probability = p)

    # m.compute()
    
    
    # m.set_loop_direction("1","r")
    # m.set_loop_direction("2","l")
    # m.set_loop_direction("3","u")
    # m.set_loop_direction("7","l")

    # _curve_doubles(m)

    # # Layout
    # ###############
    # m.set_canvas(180,100)
    # pre_layout = nx.kamada_kawai_layout(m, weight = 1)
    # pre_layout = graphviz_layout(m, prog="dot", args = "-GNodesep=0.1")
    # layout = _rotate_scale_translate(pre_layout, angle = 90, 
             # stretch_x = 2, stretch_y = 2)
    # m.set_layout(layout)
    # return(m)


# def story():
    # """The chain used in the problem 10.5.6

    # Args:
        # p (float): the probability that of a single win 
        # a (int): the amount required to exit

    # Returns: 
        # a MarkovChain object
    # """
    # m = MarkovChain(title="story-01")
    
    # m.add_state("22",label="{2,2}");
    # m.add_state("21b",label="{2,1,b}");
    # m.add_state("12r",label="{1,2,r}");
    # m.add_state("11r",label="{1,1,r}");
    # m.add_state("11b",label="{1,1,b}");
    # m.add_state("02r",label="{0,2,r}");
    # m.add_state("01r",label="{0,1,r}");
    # m.add_state("10b",label="{1,0,b}");
    # m.add_state("01b",label="{0,1,b}");
    # m.add_state("00",label="{0,0}");


    # m.add_transition("22","21b",probability = 0.5, label="1/2");
    # m.add_transition("22","12r",probability = 0.5, label="1/2");
    # m.add_transition("21b","21b",probability = 1/3, label="1/3");
    # m.add_transition("21b","11r",probability = 2/3, label="2/3");
    # m.add_transition("12r","11b",probability = 2/3, label="2/3");
    # m.add_transition("12r","02r",probability = 1/3, label="1/3"); 
    # m.add_transition("11r","01r",probability = 0.5, label="1/2");
    # m.add_transition("11r","10b",probability = 0.5, label="1/2"); #
    # m.add_transition("11b","11b",probability = 0.5, label="1/2");
    # m.add_transition("11b","01r",probability = 0.5, label="1/2");
    # m.add_transition("02r","01b",probability = 1, label="1");
    # m.add_transition("01r","00",probability = 1, label="1");
    # m.add_transition("10b","00",probability = 1, label="1");
    # m.add_transition("01b","01b",probability = 1, label="1");
    # m.add_transition("00","00",probability = 1, label="1");

    # m.set_loop_direction("21b","-60")
    # m.set_loop_direction("11b","d")



    # m.compute();

    # # Layout
    # ###############
    # m.set_canvas(180,110)
    # pre_layout = graphviz_layout(m, prog="dot", args = "-GNodesep=2")
    # layout = _rotate_scale_translate(pre_layout, angle = -90)
    # m.set_layout(layout)
    # return(m)


def _largest_initial(sofar, pat):
    assert len(pat) >= len(sofar), "Something wrong."
    if pat == sofar:
        return(True, pat)
    else:
        s = list(sofar)
        p = list(pat)
        while s:
            if s == p[:(len(s))]:
                break
            s.pop(0)
        bigger = len(s) == len(sofar)
        return(bigger, "".join(s))

def patterns(pat = "HTH"):
    """A chain used to analyze coin-tossing patterns

    Args:
        pat (str): a string pattern consisting of Hs and Ts
    """

    m=MarkovChain(title = "Patterns")

    for i in range(1,len(pat)):
        m.add_state(pat[:i], position = [30*i,0])
    m.add_state("",position = [0,0])
    m.add_state(pat,position = [30*len(pat),0], color = "orange")
    m.add_transition(pat,pat)
    for s in m.states():
        if not s == pat:
            biggerT, sT = _largest_initial(s+"T", pat)
            biggerH, sH = _largest_initial(s+"H", pat)
            extraT = len(s)+1 -  len(sT) 
            extraH = len(s)+1 -  len(sH) 
            if biggerT: extraT = 0;
            if biggerH: extraH = 0;
            m.add_transition(s,sT,probability=0.5, 
                    label="1/2", curve = -0.15*math.sqrt(extraT))
            m.add_transition(s,sH,probability=0.5, 
                    label="1/2", curve = -0.15*math.sqrt(extraH))
    m.set_name("","0")
    m.set_name(pat,"Win")
    m.set_label("0","0")
    m.set_label("Win","Win")
    for s in m.states():
        m.set_loop_direction(s,"u")
    m.set_canvas(50*len(pat),50)
    _curve_doubles(m, curve = -0.15)
    m.compute()
    return(m)

def patterns_HHH():
    """A chain used to analyze coin-tossing patterns"""

    m=MarkovChain(title = "Patterns")
    states = ["0","H","HH","Win"]
    for i,s in enumerate(states):
        m.add_state(s, position = [float(i),0])
    m.set_color("Win","orange")
    m.add_transition("0","0", probability = 0.5, label = "1/2")
    m.add_transition("0","H",probability = 0.5, label = "1/2")
    m.add_transition("H","0",probability = 0.5, label = "1/2", curve = 0.3)
    m.add_transition("H","HH",probability = 0.5, label = "1/2")
    m.add_transition("HH","0",probability = 0.5, label = "1/2", curve = -0.3)
    m.add_transition("HH","Win",probability = 0.5, label = "1/2")
    m.add_transition("Win","Win")

    m.set_loop_direction("0","u")
    m.set_loop_direction("H","u")
    m.set_loop_direction("Win","u")

    m.set_canvas(180,50)
    m.compute()
    return(m)
