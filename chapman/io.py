import os
import sys
import subprocess
import networkx as nx
from network2tikz import plot
import numpy as np
import ast
from wand.image import Image as WImage
from chapman.base import *


def write_dot(m, file_name=None):
    """Outputs a Markov chain into a dot-format file. The file name
    defaults to the chain title + ".dot"."""
    if not file_name:
        file_name = m.title+".dot"

    nx.drawing.nx_agraph.write_dot(m.graph, file_name)


def read_dot(file_name):
    """Reads a Markov chain from a "dot" file"""

    g = nx.drawing.nx_agraph.read_dot(file_name)
    # "weight" from string into float
    weight_str = nx.get_edge_attributes(g, "weight")
    weight_float = {k: float(v) for k, v in weight_str.items()}
    nx.set_edge_attributes(g, weight_float, "weight")
    m = Markov()
    m.graph = g
    return(m)

def write_tex(m, file_name=None, vertex_size=11, margin=15, **kwargs):
    """Outputs a Markov chain object in a TikZ/LaTeX format. The file name
    defaults to the chain title + ".tex" """
    g = nx.DiGraph(m)

    # process directions for loops
    updown_offset = 0
    direction_dict = {
        "u": 90+updown_offset,
        "d": -90+updown_offset,
        "l": 180+updown_offset,
        "r": 0+updown_offset,
        "ul": 135+updown_offset,
        "ur": 45+updown_offset,
        "dl": -135+updown_offset,
        "dr": -45+updown_offset
    }

    def direction_map(v):
        if v in direction_dict:
            return(direction_dict[v])
        else:
            return(v)

    loop_dict_raw = nx.get_node_attributes(g, 'loop')
    loop_dict = {(k, k): direction_map(v)
                 for k, v in loop_dict_raw.items()}

    # process positions
    layout_dict_raw = nx.get_node_attributes(g, 'position')
    layout_dict = layout_dict_raw
    # layout_dict = {k: ast.literal_eval(v)
    # for k,v in layout_dict_raw.items()}

    # process curves
    curve_dict_raw = nx.get_edge_attributes(g, 'curve')
    curve_dict = {(k[0], k[1]): float(v) for k, v in curve_dict_raw.items()}

    # process edge labels
    label_dict_raw = nx.get_edge_attributes(g, 'label')
    label_dict = {(k[0], k[1]): v for k, v in label_dict_raw.items()}

    # process colors
    def color_map(n):
        if n == 'blue' or n == '0':
            return("blue!20!white")
        else:
            return("orange!50!white")

    color_dict_raw = nx.get_node_attributes(g, 'color')
    color_dict = {k: color_map(v) for k, v in color_dict_raw.items()}
    
    # process shapes
    def shape_map(n):
        if n == 0:
            return("circle")
        else:
            return("rectangle")

    shape_dict_raw = nx.get_node_attributes(g, 'shape')
    shape_dict = {k: shape_map(v) for k, v in shape_dict_raw.items()}

    # process canvas size

    # node styles
    visual_style = {}
    visual_style['vertex_size'] = vertex_size
    visual_style['vertex_shape'] = shape_dict
    visual_style['vertex_label'] = nx.get_node_attributes(g, 'label')
    visual_style['unit'] = 'mm'
    visual_style["layout"] = layout_dict
    visual_style["canvas"] = m.canvas
    visual_style['keep_aspect_ratio'] = True
    visual_style['vertex_color'] = color_dict
    visual_style['vertex_label_color'] = 'black'
    visual_style['vertex_label_size'] = 3.5
    visual_style['vertex_math_mode'] = False
    visual_style['margin'] = margin

    # edge styles
    visual_style['edge_color'] = 'black'
    visual_style['edge_curved'] = curve_dict
    visual_style['edge_label'] = label_dict
    visual_style['edge_label_size'] = 3.5
    visual_style['edge_arrow_size'] = .2
    visual_style['edge_arrow_width'] = .2
    visual_style['edge_loop_size'] = 20
    visual_style['edge_math_mode'] = True
    visual_style['edge_loop_position'] = loop_dict

    # Create a latex file and compile it
    # strip extension first
    if not file_name:
        file_name = m.title
    file_name = os.path.splitext(file_name)[0]

    plot(g, file_name+".tex", **visual_style)


def view(m, file_name=None, **kwargs):
    """Output the chain graph in a pdf format (via Latex/Tikz). The file
    name defaults to the chain title+".pdf" """
    if not file_name:
        file_name = m.title
    # strip extension
    file_name = os.path.splitext(file_name)[0]
    write_tex(m, file_name+".tex", **kwargs)
    texcommand = "pdflatex " + file_name+".tex"
    subprocess.run(texcommand, shell=True)
    for ext in ['aux', 'log']:
        subprocess.run("rm ./"+file_name+"."+ext, shell=True)
    subprocess.run("open "+file_name+".pdf", shell=True)


def display_pdf(m, file_name=None):
    """Used to display the (already built) pdf file in Jupyter"""
    if not file_name:
        file_name = m.title+".pdf"
    return(WImage(filename=file_name))
