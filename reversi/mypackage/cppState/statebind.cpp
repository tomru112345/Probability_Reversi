#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "state.hpp"

using namespace std;

PYBIND11_MODULE(cppState, m)
{
    pybind11::class_<State>(m, "State")
        .def(pybind11::init<vector<int>>())
        .def(pybind11::init<vector<int>, vector<int>, vector<int>, int>())
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
}