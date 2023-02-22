#!/usr/bin/env python3

"""
visualizers.py

Functions to enable visualizations of graph data, starting with graphviz,
and extensible to other libraries.

"""

from graphviz import Digraph # pyright: ignore [reportMissingTypeStubs]
from simple_graph_sqlite import database as db
import json
from pathlib import Path
from typing import Callable
from sqlite3 import Cursor

def _as_dot_label(body: db.Json, exclude_keys: list[str], hide_key_name: bool, kv_separator: str):
    keys = [k for k in body.keys() if k not in exclude_keys]
    fstring = '\\n'.join(['{'+k+'}' for k in keys]) if hide_key_name else '\\n'.join(
        [k+kv_separator+'{'+k+'}' for k in keys])
    return fstring.format(**body)


def _as_dot_node(body: db.Json, exclude_keys: list[str]=[], hide_key_name: bool=False, kv_separator:str=' '):
    name = body['id']
    exclude_keys.append('id')
    label = _as_dot_label(body, exclude_keys, hide_key_name, kv_separator)
    return str(name), label


def graphviz_visualize(db_file: Path, dot_file: Path, path:list[str|int]=[], connections:Callable[[str|int], Callable[[Cursor], list[tuple[str, str, str]]]]=db.get_connections, format: str='png',
                       exclude_node_keys:list[str]=[], hide_node_key:bool=False, node_kv:str=' ',
                       exclude_edge_keys:list[str]=[], hide_edge_key:bool=False, edge_kv:str=' '):

    ids:list[str] = []
    for i in path:
        ids.append(str(i))
        for edge in db.atomic(db_file, connections(i)):
            src, tgt, _ = edge
            if src not in ids:
                ids.append(src)
            if tgt not in ids:
                ids.append(tgt)

    dot = Digraph()

    visited:list[str] = []
    edges:list[tuple[str, str, str]] = []
    for i in ids:
        if i not in visited:
            node = db.atomic(db_file, db.find_node(i))
            name, label = _as_dot_node(
                node, exclude_node_keys, hide_node_key, node_kv)
            dot.node(name, label=label) # pyright: ignore [reportUnknownMemberType]
            for edge in db.atomic(db_file, connections(i)):
                if edge not in edges:
                    src, tgt, prps = edge
                    props = json.loads(prps)
                    dot.edge(str(src), str(tgt), label=_as_dot_label( # pyright: ignore [reportUnknownMemberType]
                        props, exclude_edge_keys, hide_edge_key, edge_kv) if props else None)
                    edges.append(edge)
            visited.append(i)

    dot.render(dot_file, format=format) # pyright: ignore [reportUnknownMemberType]


def graphviz_visualize_bodies(dot_file:Path, path:list[str|tuple[str, str, str]]=[], format:str='png',
                              exclude_node_keys:list[str]=[], hide_node_key:bool=False, node_kv:str=' ',
                              exclude_edge_keys:list[str]=[], hide_edge_key:bool=False, edge_kv:str=' '):
    dot = Digraph()
    current_id = None
    edges: list[tuple[str, str, str]] = []
    for (identifier, obj, properties) in path:
        body = json.loads(properties)
        if obj == '()':
            name, label = _as_dot_node(
                body, exclude_node_keys, hide_node_key, node_kv)
            dot.node(name, label=label) # pyright: ignore [reportUnknownMemberType]
            current_id = body['id']
        else:
            edge = (str(current_id), str(
                identifier), body) if obj == '->' else (str(identifier), str(current_id), body)
            if edge not in edges:
                dot.edge(edge[0], edge[1], label=_as_dot_label( # pyright: ignore [reportUnknownMemberType]
                    body, exclude_edge_keys, hide_edge_key, edge_kv) if body else None)
                edges.append(edge)
    dot.render(dot_file, format=format) # pyright: ignore [reportUnknownMemberType]
