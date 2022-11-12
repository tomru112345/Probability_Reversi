#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "keras_model.h"
#include "state.cpp"
#include <vector>
#include <tuple>
#include <numeric>
#include <math.h>
#include <algorithm>

using namespace std;
int PV_EVALUATE_COUNT = 50;

tuple<vector<int>, int> predict(KerasModel model, State state)
{
    int a = 4;
    int b = 4;
    int c = 3;
    vector<vector<int>> tmp_l = {state.pieces, state.enemy_pieces, state.ratio_box};
    pybind11::array_t<vector<vector<int>>> x = pybind11::array_t<vector<vector<int>>>(tmp_l);
    x = x.reshape(c, a, b).transpose(1, 2, 0).reshape(1, a, b, c);
    pybind11::array_t<float> y = model.predict(x, batch_size = 1);
    struct result_t
    {
        vector<int> p;
        int v;
    };
    vector<int> tmp_act = {state.legal_actions()};
    vector<int> policies = y[0][0][tmp_act];
    int sum_policies = accumulate(policies.begin(), policies.end(), 0);
    for (int i = 0; i < policies.size(); i++)
    {
        if (sum_policies > 0)
        {
            policies.at(i) /= sum_policies;
        }
        else
        {
            policies.at(i) /= 1;
        }
    }

    int value = y[1][0][0];
    return result_t{policies, value};
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

class Node
{
private:
    KerasModel model;
    State state;
    int p = 0;
    int w = 0;
    int n = 0;

public:
    Node(KerasModel m, State s, int np)
    {
        model = m;
        state = s;
        p = np;
        vector<Node> child_nodes;
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

        if (child_node.empty())
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
                    tmp_v = -child_node.w / child_node.n;
                }
                else
                {
                    tmp_v = 0;
                }
                tmp_v += (C_PUCT * this->child_nodes.at(i).p * sqrt(t) / (1 + this->child_nodes.at(i).n));
                pucb_values.push_back(tmp_v);
            }
            vector<int>::iterator iter = max_element(pucb_values.begin(), pucb_values.end());
            int argmax_i = distance(pucb_values.begin(), iter);
            return this->child_nodes.at(argmax_i);
        }
    }
}