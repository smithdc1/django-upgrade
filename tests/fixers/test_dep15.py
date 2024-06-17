from __future__ import annotations

import sys
from functools import partial

import pytest

from django_upgrade.data import Settings
from tests.fixers import tools


settings = Settings(target_version=(5, 2))
check_noop = partial(tools.check_noop, settings=settings)
check_transformed = partial(tools.check_transformed, settings=settings)

pytestmark = pytest.mark.parametrize("original,rename", [("GET", "query_params"), ("COOKIES", "cookies")])


def test_delete(original, rename):

    check_transformed(
        f"""\
        del request.{original}['TEST']
        """, 
        f"""\
        del request.{rename}['TEST']
        """,
    )

def test_call(original, rename):
    check_transformed(
        f"""\
        query = request.{original}("q")
        """,
        f"""\
        query = request.{rename}("q")
        """,
    )

    

def test_subscript(original, rename):
    check_transformed(
        f"""\
        request.{original}["months"]
        """,
        f"""\
        request.{rename}["months"]
        """,
    )



def test_subscript_single_quotes(original, rename):
    check_transformed(
        f"""\
        request.{original}['months']
        """,
        f"""\
        request.{rename}['months']
        """,
    )

def test_get_subscript_assigned(original, rename):
    check_transformed(
        f"""\
        months = request.{original}["months"]
        """,
        f"""\
        months = request.{rename}["months"]
        """,
    )

def test_subscript_assigned_multiple(original, rename):
    check_transformed(
        f"""\
        year, months = (
            request.{original}["months"],
            request.{original}["year"],
        )
        """,
        f"""\
        year, months = (
            request.{rename}["months"],
            request.{rename}["year"],
        )
        """,
    )


def test_in(original, rename):
    check_transformed(
        f"""\
        'test' in request.{original}
        """,
        f"""\
        'test' in request.{rename}
        """,
    )
