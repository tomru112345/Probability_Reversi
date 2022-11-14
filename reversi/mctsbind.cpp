#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "mcts.hpp"

using namespace std;

// PYBIND11_MODULE(cppMCTS, m)
// {
//     m.def("predict", &predict);
//     m.def("boltzman", &boltzman);
//     m.def("pv_mcts_scores", &pv_mcts_scores);
//     m.def("pv_mcts_action", &pv_mcts_action);
// }

PYBIND11_MODULE(cppMCTS, m)
{
    pybind11::class_<MCTS>(m, "MCTS")
        .def(pybind11::init<float>())
        .def("boltzman", &MCTS::boltzman)
        .def("pv_mcts_scores", &MCTS::pv_mcts_scores);
        // .def("pv_mcts_action", &MCTS::pv_mcts_action);
}