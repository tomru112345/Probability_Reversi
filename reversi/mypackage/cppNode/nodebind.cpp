#include <pybind11/pybind11.h>
#include "node.hpp"

PYBIND11_MODULE(cppNode, m)
{
    m.def("boltzman", &boltzman);
    m.def("pv_mcts_scores", &pv_mcts_scores);
    m.def("pv_mcts_action", &pv_mcts_action);
    pybind11::class_<Node>(m, "Node")
        .def(pybind11::init())
        .def(pybind11::init<pybind11::object, State, float>())
        .def_readwrite("child_nodes", &Node::child_nodes)
        .def("append_new_child", &Node::append_new_child)
        .def("next_child_node_index", &Node::next_child_node_index)
        .def("nodes_to_scores", &Node::nodes_to_scores)
        .def("evaluate", &Node::evaluate);
}