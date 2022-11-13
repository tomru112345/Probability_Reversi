#ifndef MCTS_HPP
#define MCTS_HPP
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/embed.h>
#include "state.hpp"
#include <vector>
#include <numeric>
#include <math.h>
#include <algorithm>

using namespace std;
int PV_EVALUATE_COUNT = 50;

struct result_t
{
    vector<int> p;
    int v;
};

struct result_t predict(auto model, State state)
{
    auto pypre = pybind11::module::import("pypredict");
    auto result = pypre.attr("predict")(model, state).cast<result_t>();
    result_t res;
    res.p = result.p;
    res.v = result.v;
    return res;
}

vector<float> boltzman(vector<float> xs, float temperature)
{
    int len_xs = xs.size();
    float sum_xs = 0;
    for (int i = 0; i < len_xs; i++)
    {
        float x = xs[i];
        xs[i] = pow(x, 1 / temperature);
        sum_xs += xs[i];
    }
    vector<float> new_xs(len_xs);
    for (int i = 0; i < len_xs; i++)
    {
        new_xs[i] = 0.0;
        new_xs[i] = xs[i] / sum_xs;
    }
    return new_xs;
}

vector<float> pv_mcts_scores(auto model, State state, float temperature)
{
    class Node
    {
    private:
    public:
        State state;
        int p = 0;
        int w = 0;
        int n = 0;
        vector<Node> child_nodes;
        Node(State s, int np)
        {
            state = s;
            p = np;
            vector<Node> child_nodes;
        }

        vector<float> nodes_to_scores(vector<Node> nodes)
        {
            vector<float> scores;
            for (int i = 0; i < nodes.size(); i++)
            {
                scores.push_back(nodes.at(i).n);
            }
            return scores;
        }

        float evaluate()
        {
            float value = 0;
            if (this->state.is_done())
            {
                if (this->state.is_lose())
                {
                    value = -1;
                }
                else
                {
                    value = 0;
                }
                this->w += value;
                this->n += 1;
                return value;
            }

            if (this->child_nodes.empty())
            {
                auto result = predict(model, this->state);
                vector<int> policies = result.p;
                int value = result.v;
                this->w += value;
                this->n += 1;

                for (int i = 0; i < policies.size(); i++)
                {
                    this->child_nodes.push_back(Node(this->state.next(this->state.legal_actions().at(i)), policies.at(i)));
                }
                return value;
            }
            else
            {
                value -= this->next_child_node().evaluate();
                this->w += value;
                this->n += 1;
                return value;
            }
        }

        Node next_child_node()
        {
            float C_PUCT = 1.0;
            vector<float> scores = nodes_to_scores(this->child_nodes);
            float t = accumulate(scores.begin(), scores.end(), 0.0);

            vector<float> pucb_values;
            for (int i = 0; i < this->child_nodes.size(); i++)
            {
                if (this->child_nodes.at(i).n == 0)
                {
                    return this->child_nodes.at(i);
                }
                else
                {
                    float tmp_v;
                    if (this->child_nodes.at(i).n)
                    {
                        tmp_v = -this->child_nodes.at(i).w / this->child_nodes.at(i).n;
                    }
                    else
                    {
                        tmp_v = 0;
                    }
                    tmp_v += (C_PUCT * this->child_nodes.at(i).p * sqrt(t) / (1 + this->child_nodes.at(i).n));
                    pucb_values.push_back(tmp_v);
                }
            }
            int argmax_i = *max_element(pucb_values.begin(), pucb_values.end());
            return this->child_nodes.at(argmax_i);
        }
    };
    Node root_node = Node(state, 0);
    for (int i = 0; i < PV_EVALUATE_COUNT; i++)
    {
        root_node.evaluate();
    }

    vector<float> scores = root_node.nodes_to_scores(root_node.child_nodes);
    if (temperature == 0)
    {
        int action = *max_element(scores.begin(), scores.end());
        scores = vector<float>(scores.size(), 0);
        scores[action] = 1;
    }
    else
    {
        scores = boltzman(scores, temperature);
    }
    return scores;
}

int pv_mcts_action(auto model, State state, float temperature)
{
    vector<float> scores = get_scores(model, state);
    vector<int> leg_ac = state.legal_actions();
    auto pypre = pybind11::module::import("py_rand_choice");
    int action = pypre.attr("choice")(leg_ac, scores).cast<int>();
    return action;
}

#endif