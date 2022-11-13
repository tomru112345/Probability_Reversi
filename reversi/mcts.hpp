#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/embed.h>
#include "state.hpp"
#include "keras_model.h"
#include "node.hpp"
#include <vector>
#include <numeric>
#include <math.h>
#include <algorithm>

using namespace std;
int PV_EVALUATE_COUNT = 50;

class MCTS
{
private:
    float temperature = 0;

public:
    MCTS(float temperature)
    {
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

    vector<float> get_scores(KerasModel::KerasModel model, State state)
    {
        Node root_node = Node(model, state, 0);
        for (int i = 0; i < PV_EVALUATE_COUNT; i++)
        {
            root_node.evaluate();
        }

        vector<float> scores = root_node.nodes_to_scores(root_node.child_nodes);
        if (this->temperature == 0)
        {
            int action = *max_element(scores.begin(), scores.end());
            scores = vector<float>(scores.size(), 0);
            scores[action] = 1;
        }
        else
        {
            scores = boltzman(scores);
        }
        return scores;
    }

    int get_action(KerasModel::KerasModel model, State state)
    {
        vector<float> scores = get_scores(model, state);
        vector<int> leg_ac = state.legal_actions();
        auto pypre = pybind11::module::import("py_rand_choice");
        int action = pypre.attr("choice")(leg_ac, scores).cast<int>();
        return action;
    }
};