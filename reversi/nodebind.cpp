#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "node.cpp"
#include "state.cpp"

using namespace std;

PYBIND11_MODULE(cppNode, m)
{
    m.def("predict", &predict)
    .def("nodes_to_scores", &nodes_to_scores);
    pybind11::class_<Node>(m, "Node")
        .def(pybind11::init<auto, State, int>())
        .def("evaluate", &Node::evaluate)
        .def("next_child_node", &Node::next_child_node);
}
