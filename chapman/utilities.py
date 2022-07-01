import numpy as np

def histogram(l):
    """Tallies a list into values and relative frequencies(histogram).

    Args:
        l (list): a list 

    Returns:
        dict: a dictionary from values to frequencies
    """
    unique, counts = np.unique(l, return_counts=True)
    return(dict(zip(unique,counts/len(l))))

def _pre_print(d):
    if isinstance(d, dict):
        for k,v in sorted(d.items()):
            _pre_print(k)
            _pre_print(": ")
            _pre_print(v)
            _pre_print("\n")
    elif isinstance(d,list):
        _pre_print("[")
        for v in d:
            _pre_print(v)
            _pre_print(" ")
        _pre_print("]")
    elif isinstance(d,float):
        print(f"{d:.3f}",end="")
    else:
        print(d,end="")

def pprint(d, endchar="\n"):
    """Pretty-printts lists, dictionaries, etc. with floats rounded to 3
    decimal places.

    Args:
        d (list, dict, str, float, etc.) : the thing to be printed
        endchar (str): the final character (newline, by default)
    """

    _pre_print(d)
    print(end = endchar)


