#ifndef NODE_HPP
#define NODE_HPP

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/embed.h>
#include "state.hpp"
#include <vector>
#include <tuple>
#include <numeric>
#include <math.h>
#include <algorithm>

std::tuple<std::vector<float>, float> predict(pybind11::object model, State state)
{
    auto pypre = pybind11::module::import("pypredict");
    auto res = pypre.attr("predict")(model, state);
    std::tuple<std::vector<float>, float> tupleValue = res.cast<std::tuple<std::vector<float>, float>>();
    return tupleValue;
}

class Node
{
private:
public:
    pybind11::object model;
    State state;
    float p = 0.0;
    float w = 0.0;
    int n = 0;
    std::vector<Node> child_nodes;

    Node(pybind11::object m, State s, float np) // ノードの初期化
    {
        model = m;
        state = s;
        p = np;
        w = 0.0;
        n = 0;
        std::vector<Node> child_nodes;
    }
    float Node::evaluate();
};

std::vector<float> nodes_to_scores(std::vector<Node> nodes)
{
    vector<float> scores;
    int len_nodes = nodes.size();
    for (int i = 0; i < len_nodes; i++)
    {
        std::cout << nodes.at(i).n << " ";
        scores.push_back(nodes.at(i).n);
    }
    std::cout << endl;
    return scores;
}

#endif