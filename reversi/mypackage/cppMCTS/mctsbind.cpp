#include <pybind11/pybind11.h>
#include "mcts.cpp"

PYBIND11_PLUGIN(cppMCTS) {
    pybind11::module m("cppMCTS", "cppMCTS made by pybind11");
    m.def("boltzman", &boltzman);
    // m.def("pv_mcts_action", &pv_mcts_action);
    // m.def("pv_mcts_scores", &pv_mcts_scores);
    return m.ptr();
}