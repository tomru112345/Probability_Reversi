#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "state.hpp"

PYBIND11_MODULE(cppState, m)
{
    pybind11::class_<State>(m, "State")
        .def(pybind11::init<std::vector<int>>())
        .def(pybind11::init<std::vector<int>, std::vector<int>, std::vector<int>, int>())
        .def("set_pieces", &State::set_pieces)
        .def("set_enemy_pieces", &State::set_enemy_pieces)
        .def("set_ratio_box", &State::set_ratio_box)
        .def("set_depth", &State::set_depth)
        .def("set_pass_end", &State::set_pass_end)
        .def("get_pieces", &State::get_pieces)
        .def("get_enemy_pieces", &State::get_enemy_pieces)
        .def("get_ratio_box", &State::get_ratio_box)
        .def("get_depth", &State::get_depth)
        .def("get_pass_end", &State::get_pass_end)
        .def("get_dxy", &State::get_dxy)
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