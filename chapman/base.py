# -*- coding: utf-8 -*-
import networkx as nx
import numpy as np
import chapman._classes
import chapman._representation

DEFAULT_COLOR = "blue"

class MarkovChain(nx.DiGraph):
    """Basic Markov-chain class.
    
    MarkovChain is derived from the DiGraph class from networkx. It uses
    DiGraph to store states (nodes) and transitions (edges), as well as 
    some of their attributes. In addition to the data kept by DiGraph, it
    computes and stores information about various chain-theoretic
    properties. 

    Args:
        title (str): the title of the chain (optional, default "Untitled")
    """

    # basic methods
    def __init__(self, title="Untitled", **kwargs):

        # general
        nx.DiGraph.__init__(self, **kwargs)
        self.title = title

        # aliases for DiGraph members
        self.states = self.nodes 
        self.transitions = self.edges
        self.number_of_states = self.number_of_nodes # a function 
        self.number_of_transitions = self.number_of_edges # a function!


        # Markov-chain specific
        self.classes = []
        self.transient_states = []
        self.recurrent_states = []
        self.number_of_transient_states = None
        self.number_of_recurrent_states = None
        
        self.transient_state_indices = []
        self.recurrent_state_indices = []
        self.transient_class_indices = []
        self.recurrent_class_indices = []

        self.number_of_classes = None
        self.recurrent_classes = [] 
        self.transient_classes = [] 
        self.number_of_transient_classes = None
        self.number_of_recurrent_classes = None

        self.is_irreducible = None
        self.no_transient = None
        self.is_aperiodic = None

        self.P = None
        """Contains the transition matrix P of the chain"""
        self.Q = None
        """Contains the TxT matrix Q"""
        self.R = None
        """Contains the TxC matrix Q"""
        self.F = None
        """Contains the fundamental matrix F = (I-Q)^{-1}."""

        # index-to-state dictionaries
        self.I_to_S = {}
        """A dictionary that translates indices in P to state names"""
        self.S_to_I = {}
        """A dictionary that translates state names to indices in P"""
        self.T_to_S = {}
        """A dictionary that translates indices in T to state names"""
        self.C_to_S = {}
        """A dictionary that translates indices in C to state names"""
        self.S_to_T = {}
        """A dictionary that translates transient state names to indices in T"""
        self.S_to_C = {}
        """A dictionary that translates recurrent state names to indices in C"""

        # internal flags
        self._classes_computed = False
        self._P_matrix_computed = False
        self._QRF_matrix_computed = False

        # esthetics
        self.canvas = [150, 120]

    def add_state(self, state, label=None, color=DEFAULT_COLOR,
                  position=None, process=True, **kwargs):
        """Adds a state to a Markov chain. 

        Args:
            state (str): a string representing a state. 
        """
        # default/random label and position
        if not label:
            label = str(state)
        if not position:
            position = np.random.random(size=2)*self.canvas

        self.add_node(state, label=label, 
                position=position, color = color, **kwargs)

        self._classes_processed = False
        self._matrix_computed = False
        self._QRF_matrix_computed = False

    def add_transition(self, state1, state2, probability = 1,
                       curve=0.0, label=None, **kwargs):
        """Adds a transition to a Markov Chain. 

        A transition with probability given by the argument probability ias
        added to the chain. If no probability is given, it will default to
        1. 

        args:
            state1 (str): the initial state 
            state2 (str): the terminal state 
            probability (float): the probability of the transition (defaults to 1).
        """
        assert probability > 0, \
            "A transition must have a positive probability."

        if not label:
            label = str(probability)

        if state1 not in self.states:
            self.add_state(state1)
        if state2 not in self.states:
            self.add_state(state2)

        self.add_edge(state1, state2,
                      curve=curve, weight=probability, label=label,
                      **kwargs)

        self._classes_processed = False
        self._matrix_computed = False
        self._QRF_matrix_computed = False

   
    def is_transient(self, state):
        """Checks whether the state is transient. The chain must be
        "computed" first.

        Args: 
            state (str): 

        Returns:
            bool: The return value. 
        """
            
        if not self._classes_computed:
            _compute_classes(self)
        return(self.nodes[state]["type"] == "T")

    def is_recurrent(self, state):
        """Checks whether the state is recurrent. The chain must be
        "computed" first.

        Args: 
            state (str): 

        Returns:
            bool: The return value. 
        """
        if not self._classes_computed:
            _compute_classes(self)
        return(self.nodes[state]["type"] == "R")

    def list_of_states(self):
        """Returns the list of all states in the chain."""
        return(self.states())
    
    def list_of_transitions(self):
        """Returns the list of all transitions (pairs or states) the chain."""
        return(self.states())

    def period(self, state):
        """Returns the period of the state. The chain must be "computed" first.

        Args: 
            state (str): 

        Returns:
            int: The period of "state".
        """
        if not self._classes_computed:
            _compute_classes(self)
        return(self.nodes[state]["period"])

    def class_number(self, state):
        """ Returns the index of the class of the state in the 
        list m.classes. The chain must be "computed" first. 

        Args:
            state (str):

        Returns:
            int: the index of the class containing state.
        """
        if not self._classes_computed:
            _compute_classes(self)
        return(self.nodes[state]["class"])

    def compute(self):
        """ Performs various computations on a MarkovChain class. It
        computes periods of all states, classifies them, finds, transient
        and recurrent states, and produces the matrices P, Q, R and F (if
        they exist).
        """
        chapman._classes._compute_P_matrix(self)
        chapman._classes._compute_classes(self)
        if not self.no_transient:
            chapman._classes._compute_QRF_matrices(self)

    def _dump_states(self):
        out = ""
        state_records = self.states(data=True)
        for record in state_records:
            out += record[0]+"\n"
            for k, v in record[1].items():
                out += f"  {k}: {v}\n"
            out += "\n"
        return(out)

    def _dump_transitions(self):
        out = ""
        transition_records = self.transitions(data=True)
        for record in transition_records:
            out += record[0]+" -> "+record[1]+"\n"
            for k, v in record[2].items():
                out += f"  {k}: {v}\n"
            out += "\n"
        return(out)

    # re-setting attributes
    def set_probability(self, state1, state2, probability):
        """Sets the probability of an already existing transition. Should not
        be used unless you want to modify an existing transition. If
        probability=0, this removes the transition. 

        Args:
            state1 (str): the initial state
            state2 (str): the terminal state
            probability (float): the new probability of the transition.
        """
        if float(probability) == 0.0:
            self.remove_edge(state1, state2)
        else:
            self[state1][state2]["probability"] = probability
            self[state1][state2]["weight"] = probability

    def set_name(self, state, name):
        """Sets the name of an already existing state. Should not
        be used unless you want to modify an existing chain.

        Args:
            state1 (str): the initial state
        """
        nx.relabel_nodes(self, {state: name}, copy=False)

    def set_label(self, state, label):
        self.states[state]["label"] = label

    # setting aesthetic attributes
    def set_loop_direction(self, state, dir):
        #"""sets the loop direction for a state"""
        self.nodes[state]["loop"] = dir

    def set_color(self, state, color):
        #"""sets the color for a state """
        self.nodes[state]["color"] = color
    
    # def set_position(self, state, pos):
        # #"""sets the position if a state """
        # self.nodes[state]["position"] = color
    
    def set_canvas(self, l0, l1):
        #"""sets the canvas dimensions """
        self.canvas = [l0,l1]

    def set_curve(self, state1, state2, curve):
        #"""sets the curvature value for a transition"""
        self.edges[state1, state2]["curve"] = curve
  
    def set_layout(self, layout):
        # """Sets layout data from a dictionary

        # args:
            # layout (dict): a dictionary from states to arrays 
                # [x,y] of floats (coordinates)

        # """
        for state in layout:
            self.states[state]["position"]= layout[state]

    # dictionaries to vectors
    def dict_to_T_column(self, dct, value_for_omitted=0):
        """Returns a column vector of size T, whose values are taken from
        the dictionary dict from transient states to numbers. The value
        value_for_omitted (which defaults to 0) will be used for 
        states not included in dct.

        Args:
            dct (dict): a dictionary from strings to numbers
            value_for_omitted (int or float): used for missing states
        """

        return(np.array(
            [ [ dct.get(self.T_to_S[i], value_for_omitted) ] 
                for i in range(self.number_of_transient_states) ]
            ))
    
    def dict_to_T_row(self, dct, value_for_omitted=0):
        """Returns a row vector of size T, whose values are taken from
        the dictionary dict from transient states to numbers. The value
        value_for_omitted (which defaults to 0) will be used for 
        states not included in dct. 

        Args:
            dct (dict): a dictionary from strings to numbers
            value_for_omitted (int or float): used for missing states
        """
        return(np.array(
            [ dct.get(self.T_to_S[i], value_for_omitted) 
                for i in range(self.number_of_transient_states) ]
            ))
    

    def dict_to_P_row(self, dct, value_for_omitted=0):
        """Returns a row vector of size P (total number of states), whose
        values are taken from the dictionary dict from states to
        numbers. The value value_for_omitted (which defaults to 0) will be
        used for states not included in dct. 

        Args:
            dct (dict): a dictionary from strings to numbers
            value_for_omitted (int or float): used for missing states
        """
        return(np.array(
            [  dct.get(self.I_to_S[i], value_for_omitted)  
                for i in range(self.number_of_states()) ]
            ))
    
    def dict_to_P_column(self, dct, value_for_omitted=0):
        """Returns a row vector of size P (total number of states), whose
        values are taken from the dictionary dict from states to
        numbers. The value value_for_omitted (which defaults to 0) will be
        used for states not included in dct. 

        Args:
            dct (dict): a dictionary from strings to numbers
            value_for_omitted (int or float): used for missing states
        """
        return(np.array(
            [ [ dct.get(self.I_to_S[i], value_for_omitted) ] 
                for i in range(self.number_of_states()) ]
            ))
    def P_to_dict(self, vct):
        """Returns a dictionary from states to values, built from the 
        vector vct, according to the internal order of states of P. 

        Args:
            vct(list of numbers): a list of values, of size P.

        Returns:
            dict: a dictionary from states to values
        """
        v = np.ravel(vct)
        return( { self.I_to_S[i] : val for i,val in enumerate(v) })
    
    def T_to_dict(self, vct):
        """Returns a dictionary from transient states to values, built from the 
        vector vct, according to the internal order of states of T. 

        Args:
            vct(list of numbers): a list of values, of size P.

        Returns:
            dict: a dictionary from states to values
        """
        v = vct.flatten()
        return( { self.T_to_S[i] : val for i,val in enumerate(v) })
    
    def C_to_dict(self, vct):
        """Returns a dictionary from recurrent states to values, built from the 
        vector vct, according to the internal order of states of C.

        Args:
            vct(list of numbers): a list of values, of size P.

        Returns:
            dict: a dictionary from states to values
        """
        v = vct.flatten()
        return( { self.C_to_S[i] : val for i,val in enumerate(v) })

    def stationary_of_class(self, s):
        """Returns a dictionary states in the class of s to corresponding
        values of the stationary distribution.

        Args:
            s (str): a state

        Returns:
            dict: a dictionary from states to floats
        """
        return(chapman._classes._stationary_of_class(self, s))

    # list of recurrent classes as separate chains
    def recurrent_as_chains(self):
        """Returns a list of MarkovChain objects, each of which contains
        a single recurrent class.

        Returns:
            : a list of MarkovChain objects
        """
        return(chapman._classes._recurrent_chains(self))

            
    
    # representation/information

    def info(self):
        """Gives basic info about chain (states and transitions only).

        Returns: 
            str: returns a formatted string. Looks best when printed (as in print(m.info()))
        """
        return(chapman._representation.info(self))
    
    def info_classes(self):
        """Gives info about the class structure of the chain.

        Returns: 
            str: returns a formatted string. Looks best when printed (as in
            print(m.info_classes()))
        """
        return(chapman._representation.info_classes(self))
    
    def info_stationary(self):
        """Gives info about the stationary distributions for each
        recurrent class.

        Returns: 
            str: returns a formatted string. Looks best when printed (as in
            print(m.info_stationary()))
        """
        return(chapman._representation.info_stationary(self))
   
    def info_P(self):
        """Info about the transition matrix P and the order of states.

        Returns: 
            str: returns a formatted string. Looks best when printed (as in
            print(m.info_P()))
        """
        return(chapman._representation.info_P(self))
  
    def info_QRF(self):
        """Info about the matrices Q and R, as well as the 
        fundamental matrix F. 

        Returns: 
            str: returns a formatted string. Looks best when printed (as in
            print(m.info_QRF()))
        """
        return(chapman._representation.info_QRF(self))

    def info_all(self):
        """All available info about the chain.

        Returns: 
            str: returns a formatted string. Looks best when printed (as in
            print(m.info_all()))
        """
        infos = [ self.info(),
                self.info_classes(),
                self.info_stationary(),
                self.info_P(),
                self.info_QRF()
                ]
        return("\n".join(infos))


