#ifndef MCTS_HPP
#define MCTS_HPP
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/embed.h>
#include <iostream>
#include "state.hpp"
#include <vector>
#include <tuple>
#include <numeric>
#include <math.h>
#include <algorithm>

using namespace std;
int PV_EVALUATE_COUNT = 50;

tuple<vector<float>, float> predict(pybind11::object model, State state)
{
    auto pypre = pybind11::module::import("pypredict");
    auto res = pypre.attr("predict")(model, state);
    tuple<vector<float>, float> tupleValue = res.cast<tuple<vector<float>, float>>();
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
    vector<Node> child_nodes;

    Node(pybind11::object m, State s, float np)
    {
        model = m;
        state = s;
        p = np;
        w = 0.0;
        n = 0;
        vector<Node> child_nodes;
    }

    vector<float> nodes_to_scores()
    {
        vector<float> scores;
        int len_nodes = this->child_nodes.size();
        for (int i = 0; i < len_nodes; i++)
        {
            scores.push_back(this->child_nodes.at(i).n);
        }
        return scores;
    }

    float evaluate()
    {
        float value = 0.0;
        if (this->state.is_done())
        {
            if (this->state.is_lose())
            {
                value = -1.0;
            }
            else
            {
                value = 0.0;
            }
            this->w += value;
            this->n += 1;
            return value;
        }

        if (this->child_nodes.empty())
        {
            tuple<vector<float>, float> result = predict(this->model, this->state);
            vector<float> policies = get<0>(result);
            value = get<1>(result);
            this->w += value;
            this->n += 1;

            int len_policies = policies.size();
            for (int i = 0; i < len_policies; i++)
            {
                int action = this->state.legal_actions().at(i);
                State next_state = this->state.next(action);
                float policy = policies.at(i);
                this->child_nodes.push_back(
                    Node(this->model, next_state, policy));
            }
            return value;
        }
        else // 子ノードが存在する時
        {
            value = -(next_child_node().evaluate());
            this->w += value;
            this->n += 1;
            return value;
        }
    }

    Node next_child_node()
    {
        float C_PUCT = 1.0;
        vector<float> scores = nodes_to_scores();
        float t = 0.0;
        for (int i = 0; i < scores.size(); i++)
        {
            t += scores.at(i);
        }
        vector<float> pucb_values;
        int len_child_nodes = this->child_nodes.size();
        for (int i = 0; i < len_child_nodes; i++)
        {
            float tmp_v;
            if (this->child_nodes.at(i).n != 0)
            {
                tmp_v = -this->child_nodes.at(i).w / this->child_nodes.at(i).n;
            }
            else
            {
                tmp_v = 0.0;
            }
            tmp_v += (C_PUCT * this->child_nodes.at(i).p * sqrt(t) / (1 + this->child_nodes.at(i).n));
            pucb_values.push_back(tmp_v);
        }
        int argmax_i = *max_element(pucb_values.begin(), pucb_values.end());
        return this->child_nodes.at(argmax_i);
    }
};

vector<float> boltzman(vector<float> xs, float temperature)
{
    float sum_xs = 0;
    int len_xs = xs.size();
    for (int i = 0; i < len_xs; i++)
    {
        float x = xs[i];
        xs[i] = pow(x, 1 / temperature);
        sum_xs += x;
    }
    vector<float> new_xs(len_xs, 0.0);
    for (int i = 0; i < len_xs; i++)
    {
        new_xs[i] = xs[i] / sum_xs;
    }
    return new_xs;
}

vector<float> pv_mcts_scores(pybind11::object model, State state, float temperature)
{
    Node root_node = Node(model, state, 0);
    for (int i = 0; i < PV_EVALUATE_COUNT; i++)
    {
        root_node.evaluate();
    }
    vector<float> scores = root_node.nodes_to_scores();
    if (temperature == 0)
    {
        int action = *max_element(scores.begin(), scores.end());
        scores = vector<float>(scores.size(), 0.0);
        scores[action] = 1;
    }
    else
    {
        scores = boltzman(scores, temperature);
    }
    return scores;
}

int pv_mcts_action(pybind11::object model, State state, float temperature)
{
    vector<int> leg_ac = state.legal_actions();
    vector<float> scores = pv_mcts_scores(model, state, temperature);
    auto pypre = pybind11::module::import("py_rand_choice");
    int action = pypre.attr("choice")(leg_ac, scores).cast<int>();
    return action;
}
#endif
