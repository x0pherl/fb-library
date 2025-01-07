from dataclasses import dataclass, field
from enum import Enum, auto
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import pytest
from unittest.mock import patch
from pathlib import Path

from build123d import BuildPart, Box, Part, Sphere, Align, Mode, Location

from click_fit import divot


class TestClickfit:
    def test_divot(self):
        hole = divot(10, False)
        assert hole.is_valid()
        bump = divot(10, True)
        assert bump.is_valid()

    def test_direct_run(self):

        loader = SourceFileLoader("__main__", "src/fb_library/click_fit.py")
        loader.exec_module(
            module_from_spec(spec_from_loader(loader.name, loader))
        )
