Usage
-----

Basic usage
~~~~~~~~~~~

Don't forget to import the package before you use it

.. doctest::

    import chapman as mk 

The main player in all of this is a 

.. doctest::

    m = mk.MarkovChain(title = "My First Chain")

The title is optional (defaults to "Untitled") but it is good practice to
give your Markov chains distinctive names. Once we have instantiated the
:class:`MarkovChain` object :obj:`m`, we can start adding some states to it. 
This is accomplished by using the method :meth:`add_state`. 

.. warning:: `Markov Chain` is a class derived from `nx.DiGraph`, so it inherited its methods, such as `add_node` or `add_edge`. Do not use those. If you do no error will be reported, and it will be difficult to debug your code when it fails.

While not strictly necessary, it is a good idea to use strings - delimited by 
`" "`, or `' '` -  as state names:

.. doctest::

    >>> m.add_state("A")
    >>> m.add_state("B")
    >>> m.add_state("Stop")

The chain now contains three states. To display the contents of the chain, we
use the method :meth:`info`. It returns a string, so we need to print it:

.. doctest::

    >>> print(m.info())
    Basic info for: "My First Chain"
    --------------------------------

         - states (3): ['A', 'B', 'Stop']

         - transitions (0):

Next, we need to add the transition probabilities between states using the
method :meth:`add_transition`

.. doctest::

    >>> m.add_transition("A","B", probability = 0.5)
    >>> m.add_transition("A","A", probability = 0.5)
    >>> m.add_transition("B","A", probability = 0.5)
    >>> m.add_transition("B","Stop", probability = 0.5)
    >>> m.add_transition("Stop","Stop")

Our chain now contains some arrows between states, as well. It is not
complete, yet, though. When we are done with all the states and
transitions, we need to :meth:`compute` the chain to update its internals,
determine the classes, transient and recurrent states, periods, etc. This
will also create the chain's transition matrix. If we don't
:meth:`compute` first, an error will be reported when we try to call 
the method :meth:`info_P` which outputs the chain's transition matrix:

.. doctest::

    >>> print(m.info_P())
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/Users/gordanz/chapman/chapman/base.py", line 422, in info_P
        return(chapman._representation.info_P(self))
      File "/Users/gordanz/chapman/chapman/_representation.py", line 54, in info_P
        assert m._P_matrix_computed, "Compute the matrix P first."
    AssertionError: Compute the matrix P first.

    >>> m.compute()
    >>> print(m.info_P())
    P-matrix info for: "My First Chain"
    -----------------------------------
     - transition matrix:
    [[0.5 0.5 0. ]
     [0.5 0.  0.5]
     [0.  0.  1. ]]

     - order of states:{0: 'A', 1: 'B', 2: 'Stop'}


When building a chain, it is important to make sure that the
probabilities corresponding to all transitions from each state sum up to 1.
This is checked by :meth:`compute` and an error is reported if a
discrepancy is found. 
The
error message will supply a clue about the missing transitions by computing
the deviation from stochasticity:

.. doctest::

   >>> n = mk.MarkovChain("Missing transitions")
   >>> n.add_state("A")
   >>> n.add_state("B")
   >>> n.add_transition("A","A", probability = 0.5)
   >>> n.add_transition("A","B", probability = 0.5)
   >>> n.compute()
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
     File "/Users/gordanz/chapman/chapman/base.py", line 212, in compute
       chapman._classes._compute_P_matrix(self)
     File "/Users/gordanz/chapman/chapman/_classes.py", line 21, in _compute_P_matrix
       "Deviation = "+str(deviation)
   AssertionError: Transition matrix is not stochastic. Deviation = 1.0

.. warning:: Don't forget to include the transitions from absorbing states to themselves. This is often the reason your matrix is not stochasitc.

Getting information 
~~~~~~~~~~~~~~~~~~~

Once your chain is built, you can get information about it class structure,
transience, recurrence and periodicity through the :meth:`info` method:

.. doctest::

    >>> print(m.info_classes())
    Class info for: "My First Chain"
    --------------------------------

     - the chain is aperiodic (all states have period 1).

     - the chain is not irreducible. It has 2 classes.

     - classes (2): [['Stop'], ['B', 'A']]

     - transient classes (1, T = 2): [['B', 'A']]

     - recurrent classes (1, C = 1): [['Stop']]


The method :meth:`info_P` also outputs the transition matrix, together with
the information about how states are mapped to its rows (columns). 

.. doctest::

   >>> print(m.info_P())
   P-matrix info for: "My first chain"
   -----------------------------------
    - transition matrix:
   [[0.5 0.5 0. ]
    [0.5 0.  0.5]
    [0.  0.  1. ]]

    - order of states:{0: 'A', 1: 'B', 2: 'Stop'}

The matrix P can be accessed directly through the member variable :data:`P`

.. doctest::

  >>> m.P
  array([[0.5, 0.5, 0. ],
         [0.5, 0. , 0.5],
         [0. , 0. , 1. ]])

For chains with at least one transient state, the method :meth:`info_QRF()`
outputs the matrices Q and R from the canonical decomposition, as well as
the fundamental matrix F. To be able to tell which row (column) of the
matrix corresponds to which state, two separate mappings - one for transient (T-) and one for recurrent (C-) states are also given.

.. doctest::

    >>> print(m.info_QRF())
    QRF info for: "My First Chain"
    ------------------------------

     - matrix Q (T x T):
       [[0.5 0.5]
        [0.5 0. ]]

     - matrix R (T x C):
       [[0. ]
        [0.5]]

     - fundamental matrix F=(I-Q)^-1 (T x T):
       [[4. 2.]
        [2. 2.]]

     - order of T-states: {0: 'A', 1: 'B'}

     - order of C-states: {0: 'Stop'}


Just like P, the matrices Q, R and F are available directly using members
:data:`Q`, :data:`R` and :data:`F`. All of them will be returned as `numpy`
arrays; this is important, among other things, because you can use the
symbol `@` to perform matrix multiplication

.. doctest::

     >>> m.F
    array([[4., 2.],
           [2., 2.]])
    >>> U = m.F @ m.R
    >>> U
    array([[1.],
           [1.]])


Dictionaries and vector indices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It takes three different dictionaries to translate between (all) states and
the row (column) numbers in the transitions matrix P, transient states and
the rows (columns) of Q and recurrent states and columns of R. These three
dictionaries, as well as their inverses are available directly through
members :data:`S_to_I`, :data:`I_to_S`, :data:`S_to_T`, :data:`T_to_S`, :data:`S_to_C` and :data:`C_to_S`

.. doctest::

   >>> m.S_to_I
   {'A': 0, 'B': 1, 'Stop': 2}
   >>> m.I_to_S
   {0: 'A', 1: 'B', 2: 'Stop'}
   >>> m.S_to_T
   {'A': 0, 'B': 1}
   >>> m.T_to_S
   {0: 'A', 1: 'B'}
   >>> m.S_to_C
   {'Stop': 0}
   >>> m.C_to_S
   {0: 'Stop'}

In general, we want to supply initial distributions or "reward" vectors as
dictionaries, for at least two reasons. One, we do not know a-priori which
positions correspond to which states, so we need to consult a dictionary
anyway. Two, many times, most of the entries of the vector are zeros (or
ones) and using a dictionary is a much more efficient way of supplying only
the non-trivial values. Several methods are available to help with that.
For example :meth:`dict_to_T_row` converts the dictionary from transient states
to state names to a row-vector of size T. 

.. doctest::

   >>> m.dict_to_T_row({"A": 1, "B":2})
   array([1, 2])

Missing values are automatically replaced by 0. 


.. doctest::

   >>> m.dict_to_T_row({"B":3})
   array([0, 3])

If you want some other value to be used for missing states, use the optional argument
:data:`value_for_omitted`

.. doctest::

     >>> m.dict_to_T_row({"A":3}, value_for_omitted = 1)
     array([3, 1]) 

Other similar methods, such as 
:meth:`dict_to_P_row` (used for initial distributions) or
:meth:`dict_to_T_column` (used for "reward" computations) are also
available.

.. doctest::

   >>> m.dict_to_T_column({"B":2})
   array([[0],
          [2]])


You can go the other way, too. Given a row or a column vector you get as a
result of a computation, you can check what its values on various states
are without eyeballing the exact row or column of an entry. In this case it
does not matter if the input vector is a row or a column, but it does
matter whether it represents transient or recurrent states. The three
available methods are :meth:`T_to_dict`, :meth:`C_to_dict` and
:meth:`P_to_dict`.

.. doctest::

   >>> a=m.dict_to_T_row({"A":2})
   >>> m.T_to_dict(a)
   {'A': 2, 'B': 0}


Examples
~~~~~~~~

The package :mod:`chapman` contains a module called
:mod:`chapman.examples` which contains a number of already implemented
examples from your lecture notes. To use them, you have to import it first

.. doctest::

   >>> import chapman.examples as mke

The collection of available examples will grow in time. To get the list of those available right now, use :func:`list_examples`

.. doctest::

   >>> mke.list_examples()
   ['attached_cycles', 'facility', 'gambler', 'mc20_1', 'mc21_1',
   'mc8_1', 'patterns_HHH', 'patterns_HTH', 'professor', 'tennis']


To learn more about each available example, use the builtin function
:func:`help`

.. doctest::

   >>> help(mke.tennis)
   Help on function tennis in module chapman.examples:

   tennis(p=0.4)
       The tennis chain.

       Args:
           p (float): the probability that S wins in a single rally

       Returns:
           a MarkovChain object


Finally, as in illustration, let us compute the expected number of deuces
(40-40 scores) in s single game of tennis where the probability of winning
a single rally for the two players are  0.55 and 0.45. 

.. doctest::

   >>> import chapman as mk
   >>> import chapman.examples as mke
   >>> m = mke.tennis(p=0.55)
   >>> a0_T = m.dict_to_T_row({"0-0" : 1})
   >>> g = m.dict_to_T_column({"40-40" : 1}, value_for_omitted=0)
   >>> a0_T @ m.F @ g
   array([0.6])

Note that all examples are already "computed", so you don't need to call the
:meth:`command` method. Also, note how we use the functions
:meth:`dict_to_T_row` and :meth:`dict_to_T_column` to simplify the entry of
long vectors whose values are mostly zeros. Finally, the result is
technically a 1x1 matrix - that is why we see the :func:`array()` and
:obj:`[]` around it. 


