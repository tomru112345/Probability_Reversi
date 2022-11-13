#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/embed.h>
#include "keras_model.h"
#include "state.hpp"
#include <vector>
#include <numeric>
#include <math.h>

using namespace std;

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

class Node
{
private:
public:
    auto model;
    State state;
    int p = 0;
    int w = 0;
    int n = 0;
    vector<Node> child_nodes;
    Node(auto m, State s, int np)
    {
        model = m;
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
            auto result = predict(this->model, this->state);
            vector<int> policies = result.p;
            int value = result.v;
            this->w += value;
            this->n += 1;

            for (int i = 0; i < policies.size(); i++)
            {
                this->child_nodes.push_back(Node(this->model, this->state.next(this->state.legal_actions().at(i)), policies.at(i)));
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