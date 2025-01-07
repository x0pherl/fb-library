from dataclasses import dataclass, field
from enum import Enum, auto
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import pytest
from unittest.mock import patch
from pathlib import Path

from build123d import BuildPart, Box, Part, Sphere, Align, Mode, Location

from dovetail import DovetailPart, dovetail_split_outline


class TestDovetail:

    def test_direct_run(self):

        loader = SourceFileLoader("__main__", "src/fb_library/dovetail.py")
        loader.exec_module(
            module_from_spec(spec_from_loader(loader.name, loader))
        )
