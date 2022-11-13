#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "mcts.hpp"

using namespace std;

PYBIND11_MODULE(cppMCTS, m)
{
    // pybind11::class_<MCTS>(m, "MCTS")
    //     .def(pybind11::init<float>())
    //     .def("boltzman", &MCTS::boltzman)
    //     .def("get_scores", &MCTS::get_scores)
    //     .def("get_action", &MCTS::get_action);
    m.def("predict", &predict)
    .def("boltzman", &boltzman)
    .def("pv_mcts_scores", &pv_mcts_scores)
    .def("pv_mcts_action", &pv_mcts_action);
    // pybind11::class_<Node>(m, "Node")
    //     .def(pybind11::init<auto, State, int>())
    //     .def("evaluate", &Node::evaluate)
    //     .def("nodes_to_scores", &Node::nodes_to_scores)
    //     .def("next_child_node", &Node::next_child_node);
}
