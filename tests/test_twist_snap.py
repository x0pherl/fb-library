import pytest
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from unittest.mock import patch
from pathlib import Path

from fb_library.twist_snap import (
    twist_snap_connector,
    twist_snap_socket,
)


class TestTwistSnap:
    def test_bare_execution(self):
        with (
            patch("build123d.export_stl"),
            patch("pathlib.Path.mkdir"),
            patch("pathlib.Path.exists"),
            patch("pathlib.Path.is_dir"),
            patch("ocp_vscode.show"),
            patch("ocp_vscode.save_screenshot"),
        ):
            loader = SourceFileLoader(
                "__main__", "src/fb_library/twist_snap.py"
            )
            loader.exec_module(
                module_from_spec(spec_from_loader(loader.name, loader))
            )

    def test_twist_snap_connector(self):
        connector = twist_snap_connector(
            connector_diameter=4.5,
            tolerance=0.12,
            snapfit_height=2,
            snapfit_radius_extension=2 * (2 / 3) - 0.06,
            wall_width=2,
            wall_depth=2,
        )
        assert connector.is_valid()

    def test_twist_snap_socket(self):
        socket = twist_snap_socket(
            connector_diameter=4.5,
            tolerance=0.12,
            snapfit_height=2,
            snapfit_radius_extension=2 * (2 / 3) - 0.06,
            wall_width=2,
            wall_depth=2,
        )
        assert socket.is_valid()
