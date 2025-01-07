@echo off
setlocal


SET PROJECT_NAME=fb-library

SET /P PYTEST_CHOSEN=Do you want to run pytest --cov ([Y]/N)?
IF /I "%PYTEST_CHOSEN%" NEQ "N" GOTO TEST
GOTO BUILD

:TEST
pytest --cov

SET /P PYTEST_CLEAN=Based on the pytest results, proceed with the build? ([Y]/N)?
IF /I "%PYTEST_CLEAN%" NEQ "N" GOTO BUILD

GOTO END

:BUILD
py -m pip uninstall -y %PROJECT_NAME%

py -m build
py -m pip install -e .

:TESTLOCAL
python -c "exec(\"from fb_library import dovetail_subpart, click_fit, Point, shifted_midpoint\nprint(shifted_midpoint(Point(0,0), Point(10,10),0))\")"
:END
endlocal