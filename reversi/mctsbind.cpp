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

PYBIND11_PLUGIN(cppMCTS) {
    pybind11::module m("cppMCTS", "mylibs made by pybind11");
    m.def("predict", &predict);
    m.def("boltzman", &boltzman);
    m.def("pv_mcts_scores", &pv_mcts_scores);
    m.def("pv_mcts_action", &pv_mcts_action);
    return m.ptr();
}