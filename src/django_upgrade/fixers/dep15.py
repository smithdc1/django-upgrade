"""
Renames Request attributes.

Feature TBC...
"""

from __future__ import annotations

import ast
import sys
from functools import partial
from typing import Iterable

from tokenize_rt import Offset
from tokenize_rt import Token

from django_upgrade.ast import ast_start_offset
from django_upgrade.data import Fixer
from django_upgrade.data import State
from django_upgrade.data import TokenFunc
from django_upgrade.tokens import NAME
from django_upgrade.tokens import STRING
from django_upgrade.tokens import erase_node
from django_upgrade.tokens import find
from django_upgrade.tokens import replace
from django_upgrade.tokens import str_repr_matching

fixer = Fixer(
    __name__,
    min_version=(5, 2),
)

RENAMES = {
    "GET": "query_params",
    "COOKIES": "cookies",
}


@fixer.register(ast.Assign)
def visit_Assign(
    state: State,
    node: ast.Assign,
    parents: list[ast.AST],
) -> Iterable[tuple[Offset, TokenFunc]]:
    if (
        isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Attribute)
        and isinstance(node.value.func.value.value, ast.Name)
        and node.value.func.value.value.id == "request"
        and node.value.func.value.attr in RENAMES
    ):
        attribute = node.value.func.value.attr
        yield ast_start_offset(node), partial(rewrite_get_access, attribute=attribute)


@fixer.register(ast.Subscript)
def visit_Subscript(
    state: State,
    node: ast.Subscript,
    parents: list[ast.AST],
) -> Iterable[tuple[Offset, TokenFunc]]:
    if (
        isinstance(node.value, ast.Attribute)
        and node.value.attr in RENAMES
        and node.value.value.id == "request"
    ):
        attribute = node.value.attr
        yield ast_start_offset(node), partial(rewrite_get_access, attribute=attribute)


@fixer.register(ast.Compare)
def visit_Compare(
    state: State,
    node: ast.Compare,
    parents: list[ast.AST],
) -> Iterable[tuple[Offset, TokenFunc]]:
    if (
        isinstance(node, ast.Compare)
        and len(node.ops) == 1
        and isinstance(node.ops[0], (ast.In, ast.NotIn))
        and len(node.comparators) == 1
        and isinstance(node.comparators[0], ast.Attribute)
        and node.comparators[0].attr in RENAMES
        and node.comparators[0].value.id == "request"
        and isinstance(node.left, ast.Constant)
    ):
        attribute = node.comparators[0].attr
        yield ast_start_offset(node), partial(rewrite_in_statement, attribute=attribute)


def rewrite_get_access(tokens: list[Token], i: int, *, attribute: str) -> None:
    meta_idx = find(tokens, i, name=NAME, src=attribute)
    replace(tokens, meta_idx, src=RENAMES[attribute])


def rewrite_in_statement(tokens: list[Token], i: int, *, attribute: str) -> None:
    meta_idx = find(tokens, i, name=NAME, src=attribute)
    replace(tokens, meta_idx, src=RENAMES[attribute])
