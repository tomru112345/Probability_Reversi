#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "mcts.hpp"

using namespace std;

PYBIND11_MODULE(cppMCTS, m)
{
    m.def("boltzman", &boltzman);
    m.def("pv_mcts_scores", &pv_mcts_scores);
    m.def("pv_mcts_action", &pv_mcts_action);
}