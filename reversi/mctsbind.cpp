#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "mcts.hpp"

using namespace std;

PYBIND11_MODULE(cppMCTS, m)
{
    pybind11::class_<MCTS>(m, "MCTS")
        .def(pybind11::init<auto, float>())
        .def("boltzman", &MCTS::boltzman)
        .def("get_scores", &MCTS::get_scores)
        .def("get_action", &MCTS::get_action);
}
