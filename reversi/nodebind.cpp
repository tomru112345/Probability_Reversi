#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "keras_model.h"
#include "node.cpp"
#include <iostream>
#include <vector>
#include <cstdlib>
#include <algorithm>

using namespace std;

PYBIND11_MODULE(cppNode, m)
{
    m.def("predict", &predict);
    pybind11::class_<Node>(m, "Node")
        .def(pybind11::init<KerasModel, State, int>())
        .def("evaluate", &Node::evaluate)
        .def("nodes_to_scores", &Node::nodes_to_scores)
        .def("next_child_node", &Node::next_child_node);
}
