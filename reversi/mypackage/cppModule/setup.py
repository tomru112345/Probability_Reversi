from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

__version__ = "0.0.1"

ext_modules = [
    Pybind11Extension("cppModule",
                      ["bind.cpp"],
                      language='c++',
                      define_macros=[('VERSION_INFO', __version__)],
                      ),
]

setup(
    name="cppModule",
    version=__version__,
    author="tamura kazuma",
    description="written by cpp",
    long_description="",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
)