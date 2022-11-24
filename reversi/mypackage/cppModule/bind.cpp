#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "module.cpp"

PYBIND11_MODULE(cppModule, m)
{
    
}

PYBIND11_PLUGIN(cppModule) {
    pybind11::module m("cppModule", "cppModule made by pybind11");
    pybind11::class_<State>(m, "State")
        .def(pybind11::init<std::vector<int>>())
        .def(pybind11::init<std::vector<int>, std::vector<int>, std::vector<int>, int>())
        .def_readwrite("pieces", &State::pieces)
        .def_readwrite("enemy_pieces", &State::enemy_pieces)
        .def_readwrite("ratio_box", &State::ratio_box)
        .def_readwrite("depth", &State::depth)
        .def_readwrite("dxy", &State::dxy)
        .def_readwrite("pass_end", &State::pass_end)
        .def("set_ratio", &State::set_ratio)
        .def("piece_count", &State::piece_count)
        .def("is_done", &State::is_done)
        .def("is_lose", &State::is_lose)
        .def("is_draw", &State::is_draw)
        .def("is_first_player", &State::is_first_player)
        .def("next", &State::next)
        .def("legal_actions", &State::legal_actions)
        .def("is_legal_action_xy_dxy", &State::is_legal_action_xy_dxy)
        .def("is_legal_action_xy", &State::is_legal_action_xy)
        .def("is_legal_action_xy_dxy_penalty", &State::is_legal_action_xy_dxy_penalty);
    pybind11::class_<Node>(m, "Node")
        .def(pybind11::init<pybind11::object, State, float>())
        .def_readwrite("model", &Node::model)
        .def_readwrite("state", &Node::state)
        .def_readwrite("p", &Node::p)
        .def_readwrite("w", &Node::w)
        .def_readwrite("n", &Node::n)
        .def_readwrite("child_nodes", &Node::child_nodes)
        .def("append_new_child", &Node::append_new_child)
        .def("next_child_node_index", &Node::next_child_node_index)
        .def("nodes_to_scores", &Node::nodes_to_scores)
        .def("evaluate", &Node::evaluate);
    return m.ptr();
}
