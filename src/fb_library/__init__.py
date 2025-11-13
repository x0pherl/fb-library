import warnings

warnings.warn(
    "\n ############ DEPRECATION WARNING ############ \n"
    + "\nThe fb-library package is deprecated and will no longer be maintained. \n"
    + "Please migrate your code to b3dkit (https://b3dkit.readthedocs.io/en/latest/) \n"
    + "for continued support and new features. \n"
    + "While b3dkit offers the same functionality, please note that there are \n"
    + "breaking changes to offer a more similar 'feel' to build123d. \n\n",
    DeprecationWarning,
    stacklevel=2,
)

from fb_library.basic_shapes import *
from fb_library.ball_socket import *
from fb_library.click_fit import *
from fb_library.dovetail import *
from fb_library.hexwall import *
from fb_library.high_top_slide_box import *
from fb_library.point import *
from fb_library.slide_box import *
from fb_library.twist_snap import *
from fb_library.antichamfer import *
