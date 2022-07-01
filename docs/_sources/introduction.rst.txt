Introduction
------------


:mod:`chapman` is a Python package for construction of and computation
on simple Markov chains.  It is based on the wonderful
networkx_ package which performs all of the graph-theoretic heavy lifting. The
additional, Markov-chain-specific functions are not optimized in any way,
and should not be used IRL. They should work fairly quickly for chains of
moderate size (up to 100 states, say), though. 

.. _networkx: https://networkx.github.io/ 
