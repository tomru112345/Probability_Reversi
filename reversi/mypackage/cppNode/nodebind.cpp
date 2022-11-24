#include <pybind11/pybind11.h>
#include "node.hpp"

PYBIND11_MODULE(cppNode, m)
{
    pybind11::class_<Node>(m, "Node")
    .def_readwrite("model", &Node::model)
    .def_readwrite("state", &Node::state)
    .def_readwrite("p", &Node::p)
    .def_readwrite("w", &Node::w)
    .def_readwrite("n", &Node::n)
    .def_readwrite("child_nodes", &Node::child_nodes)
    .def(pybind11::init<pybind11::object, State, float>())
    .def("append_new_child", &Node::append_new_child)
    .def("next_child_node_index", &Node::next_child_node_index)
    .def("nodes_to_scores", &Node::nodes_to_scores)
    .def("evaluate", &Node::evaluate);
}