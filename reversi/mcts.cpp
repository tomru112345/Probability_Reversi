#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "state.cpp"
#include "node.cpp"
#include <vector>
#include <tuple>
#include <numeric>
#include <math.h>
#include <algorithm>

using namespace std;

int PV_EVALUATE_COUNT = 50;

class MCTS
{
private:
    float temperature = 0;
    auto model;

public:
    MCTS(auto model, float temperature)
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

    vector<float> get_scores(State state)
    {
        Node root_node = Node(this.model, state, 0);
        for (int i = 0; i < PV_EVALUATE_COUNT; i++)
        {
            root_node.evaluate();
        }

        vector<float> scores = nodes_to_scores(root_node.child_nodes);
        if (this->temperature == 0)
        {
            vector<int>::iterator iter = max_element(scores.begin(), scores.end());
            int action = distance(scores.begin(), iter);
            scores = vector<float>(scores.size(), 0);
            scores[action] = 1;
        }
        else
        {
            scores = boltzman(scores);
        }
        return scores;
    }

    int get_action(State state)
    {
        vector<float> scores = get_scores(state);
        // TODO
        leg_ac = state.legal_actions();
        int action = scores[rand() % scores.size()];
        return action;
    }
};