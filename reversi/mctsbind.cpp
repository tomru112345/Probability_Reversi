#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "mcts.hpp"

using namespace std;

PYBIND11_MODULE(cppMCTS, m)
{
    m.def("boltzman", &boltzman);
    m.def("pv_mcts_scores", &pv_mcts_scores);
    pybind11::class_<MCTS>(m, "MCTS")
        .def(pybind11::init<float>())
        
        
        // .def("pv_mcts_action", &MCTS::pv_mcts_action);
}