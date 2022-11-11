#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "keras_model.h"
#include <vector>
#include <numeric>
#include <math.h>
#include "state.cpp"
using namespace std;
namespace py = pybind11;

// #include <Eigen/Dense>
// #include <pybind11/eigen.h>

// namespace py = pybind11;
// Eigen::MatrixXd m(2, 2);

// Eigen::MartixXd reshape(int a, int b, int c)
// {
// }

KerasModel model;
model.LoadModel("example.model");
int PV_EVALUATE_COUNT = 50;

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
    state.State state;
    int p = 0;
    int w = 0;
    int n = 0;

public:
    Node(KerasModel m, state.State s, int np)
    {
        model = m;
        state = s;
        p = np;
        vector<Node> child_nodes = NULL;
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
            this.w += value;
            this.n += 1;
            return value;
        }

        if (child_node.empty())
        {
            // TODO
            policies, value = predict(self.model, self.state);
            this.w += value;
            this.n += 1;

            for (int i = 0; i < policies.size(); i++)
            {
                this.child_nodes.push_back(Node(this->model, this->state.next(this->state.legal_actions().at(i)), policies.at(i)));
            }
            return value;
        }
        else
        {
            value -= this->next_child_node().evaluate();
            this.w += value;
            this.n += 1;
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
            return;
        }
    }
}

class MCTS
{
private:
    float temperature = 0;
    KerasModel model = NULL;

public:
    MCTS(KerasModel model, float temperature)
    {
        this->model = model;
        this->temperature = temperature;
    }

    vector<float> boltzman(vector<float> xs)
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

    vector<float> get_scores(state.State state)
    {
        Node root_node = Node(this.model, state, 0);
        for (int i = 0; i < PV_EVALUATE_COUNT; i++)
        {
            root_node.evaluate();
        }
    }
};

PYBIND11_PLUGIN(cppMCTS)
{
    py::module m("cppMCTS", "pybind11 example plugin");
    py::class_<MCTS>(m, "MCTS")
        .def(py::init<float>())
        .def("boltzman", &MCTS::boltzman);
    return m.ptr();
}
