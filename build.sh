#!/bin/bash

set -e

PROJECT_NAME="fb-library"

read -p "Do you want to run pytest --cov ([Y]/N)? " PYTEST_CHOSEN
PYTEST_CHOSEN=${PYTEST_CHOSEN:-Y}
if [[ "$PYTEST_CHOSEN" =~ ^[Yy]$ ]]; then
    pytest --cov
    read -p "Based on the pytest results, proceed with the build? ([Y]/N)? " PYTEST_CLEAN
    PYTEST_CLEAN=${PYTEST_CLEAN:-Y}
    if [[ ! "$PYTEST_CLEAN" =~ ^[Yy]$ ]]; then
        echo "Build aborted."
        exit 0
    fi
fi

# Build process
pip uninstall -y "$PROJECT_NAME" || true
rm -rf dist/*

python -m build
pip install -e .

# # Local test
python -c "from fb_library import dovetail_subpart, click_fit, Point, shifted_midpoint; print(shifted_midpoint(Point(0,0), Point(10,10),0))"

read -p "Based on that simple test, upload to PyPI? ([Y]/N)? " PYPI_UPLOAD
PYPI_UPLOAD=${PYPI_UPLOAD:-Y}
if [[ "$PYPI_UPLOAD" =~ ^[Yy]$ ]]; then
    python -m twine upload dist/*
    pip uninstall -y "$PROJECT_NAME"
    pip install "$PROJECT_NAME"
    python -c "from fb_library import dovetail_subpart, click_fit, Point, shifted_midpoint; print(shifted_midpoint(Point(0,0), Point(10,10),0))"
    echo "REMINDER!!! Commit and push git changes!!!"
else
    echo "Upload to PyPI skipped."
fi