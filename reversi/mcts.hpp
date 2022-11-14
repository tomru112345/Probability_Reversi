#ifndef MCTS_HPP
#define MCTS_HPP
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/embed.h>
// #include "state.hpp"
#include "./keras_model.h"
#include <vector>
#include <tuple>
#include <cstdlib>
#include <cmath>
#include <numeric>
#include <math.h>
#include <algorithm>

using namespace std;
int PV_EVALUATE_COUNT = 50;

class State
{
private:
    static const int center_idx = 8;
    static const int balance_idx = 2;

public:
    vector<int> pieces = vector<int>(16, 0);
    vector<int> enemy_pieces = vector<int>(16, 0);
    vector<int> ratio_box = vector<int>(16, 100);

    int depth = 0;
    vector<vector<int>> dxy = {{1, 0}, {1, 1}, {0, 1}, {-1, 1}, {-1, 0}, {-1, -1}, {0, -1}, {1, -1}};
    bool pass_end = false;

    State()
    {
        this->pieces[center_idx - balance_idx - 1] = 1;
        this->pieces[center_idx + balance_idx] = 1;
        this->enemy_pieces[center_idx - balance_idx] = 1;
        this->enemy_pieces[center_idx + balance_idx - 1] = 1;
    }

    State(vector<int> p, vector<int> ep, vector<int> r, int d)
    {
        this->pieces = p;
        this->enemy_pieces = ep;
        this->ratio_box = r;
        this->depth = d;
    }

    int piece_count(vector<int> pieces)
    {
        int cnt = 0;
        for (int i = 0; i < pieces.size(); i++)
        {
            if (pieces[i] == 1)
            {
                cnt++;
            }
        }
        return cnt;
    }

    bool is_done()
    {
        if ((piece_count(this->pieces) + piece_count(this->enemy_pieces) == 16) || this->pass_end)
        {
            return true;
        }
        else
        {
            return false;
        }
    }

    bool is_lose()
    {
        if (is_done() && (piece_count(this->pieces) < piece_count(this->enemy_pieces)))
        {
            return true;
        }
        else
        {
            return false;
        }
    }

    bool is_draw()
    {
        if (is_done() && (piece_count(this->pieces) == piece_count(this->enemy_pieces)))
        {
            return true;
        }
        else
        {
            return false;
        }
    }

    bool is_first_player()
    {
        return (this->depth % 2 == 0);
    }

    State next(int action)
    {
        State state = State(this->pieces, this->enemy_pieces, this->ratio_box, depth + 1);
        if (action != 16)
        {
            int ac_x = action % 4;
            int ac_y = action / 4;
            state.is_legal_action_xy(ac_x, ac_y, true);
        }

        vector<int> w = state.pieces;
        state.pieces = state.enemy_pieces;
        state.enemy_pieces = w;

        vector<int> pass_vec = {16};
        vector<int> leg_vec = state.legal_actions();
        if (action == 16 && leg_vec == pass_vec)
        {
            state.pass_end = true;
        }
        return state;
    }

    vector<int> legal_actions()
    {
        vector<int> actions;
        for (int j = 0; j < 4; j++)
        {
            for (int i = 0; i < 4; i++)
            {
                if (is_legal_action_xy(i, j, false))
                {
                    actions.push_back(i + j * 4);
                }
            }
        }
        if (actions.empty())
        {
            actions.push_back(16);
        }
        return actions;
    }

    bool is_legal_action_xy_dxy(int x, int y, int dx, int dy, bool flip = false)
    {
        int new_x = x;
        int new_y = y;
        new_x += dx;
        new_y += dy;
        if ((new_y < 0) || (3 < new_y) || (new_x < 0) || (3 < new_x))
        {
            return false;
        }
        else if (this->enemy_pieces[new_x + new_y * 4] != 1)
        {
            return false;
        }

        for (int j = 0; j < 4; j++)
        {
            if ((new_y < 0) || (3 < new_y) || (new_x < 0) || (3 < new_x))
            {
                return false;
            }
            else if (this->enemy_pieces[new_x + new_y * 4] == 0 && this->pieces[new_x + new_y * 4] == 0)
            {
                return false;
            }
            if (this->pieces[new_x + new_y * 4] == 1)
            {
                if (flip)
                {
                    for (int i = 0; i < 4; i++)
                    {
                        new_x -= dx;
                        new_y -= dy;
                        if (this->pieces[new_x + new_y * 4] == 1)
                        {
                            return true;
                        }
                        this->pieces[new_x + new_y * 4] = 1;
                        this->enemy_pieces[new_x + new_y * 4] = 0;
                    }
                }
                return true;
            }
            new_x += dx;
            new_y += dy;
        }
        return false;
    }

    bool is_legal_action_xy_dxy_penalty(int x, int y, int dx, int dy, bool flip = false)
    {
        x += dx;
        y += dy;
        if ((y < 0) || (3 < y) || (x < 0) || (3 < x) || (this->enemy_pieces[x + y * 4] != 1))
        {
            return false;
        }

        for (int j = 0; j < 4; j++)
        {
            if ((y < 0) || (3 < y) || (x < 0) || (3 < x) || ((this->enemy_pieces[x + y * 4] == 0) && (this->pieces[x + y * 4] == 0)))
            {
                return false;
            }
            if (this->pieces[x + y * 4] == 1)
            {
                if (flip)
                {
                    for (int i = 0; i < 4; i++)
                    {
                        x -= dx;
                        y -= dy;
                        if (this->pieces[x + y * 4] == 1)
                        {
                            return true;
                        }
                        this->pieces[x + y * 4] = 1;
                        this->enemy_pieces[x + y * 4] = 0;
                    }
                }
                return true;
            }
            x += dx;
            y += dy;
        }
        return false;
    }

    bool is_legal_action_xy(int x, int y, bool flip = false)
    {
        if (this->enemy_pieces[x + y * 4] == 1 || this->pieces[x + y * 4] == 1)
        {
            return false;
        }
        if (flip)
        {
            // this->pieces[x + y * 4] = 1;
            if (rand() % 101 <= this->ratio_box[x + y * 4])
            {
                this->pieces[x + y * 4] = 1;
            }
            else
            {
                this->enemy_pieces[x + y * 4] = 1;
                for (int i = 0; i < this->dxy.size(); i++)
                {
                    is_legal_action_xy_dxy_penalty(x, y, this->dxy[i][0], this->dxy[i][1], flip);
                }
                return false;
            }
        }
        bool flag = false;
        for (int i = 0; i < this->dxy.size(); i++)
        {
            if (is_legal_action_xy_dxy(x, y, this->dxy[i][0], this->dxy[i][1], flip))
            {
                flag = true;
            }
        }
        return flag;
    }
};

tuple<vector<int>, int> predict(pybind11::object model, State state)
{
    auto pypre = pybind11::module::import("pypredict");
    auto res = pypre.attr("predict")(model, state);
    tuple<vector<int>, int> tupleValue = res.cast<tuple<vector<int>, int>>();
    return tupleValue;
}

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

    float evaluate(pybind11::object model)
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
            tuple<vector<int>, int> result = predict(model, this->state);
            vector<int> policies = get<0>(result);
            int value = get<1>(result);
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
            value -= this->next_child_node().evaluate(model);
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
            float tmp_v;
            if (abs(this->child_nodes.at(i).n) > 0)
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
        int argmax_i = *max_element(pucb_values.begin(), pucb_values.end());
        return this->child_nodes.at(argmax_i);
    }
};

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
    vector<float> new_xs(len_xs, 0.0);
    for (int i = 0; i < len_xs; i++)
    {
        new_xs[i] = xs[i] / sum_xs;
    }
    return new_xs;
}

vector<float> pv_mcts_scores(pybind11::object model, State state, float temperature)
{
    Node root_node = Node(state, 0);
    for (int i = 0; i < PV_EVALUATE_COUNT; i++)
    {
        root_node.evaluate(model);
    }

    vector<float> scores = root_node.nodes_to_scores(root_node.child_nodes);
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
    vector<float> scores = pv_mcts_scores(model, state, temperature);
    vector<int> leg_ac = state.legal_actions();
    auto pypre = pybind11::module::import("py_rand_choice");
    int action = pypre.attr("choice")(leg_ac, scores).cast<int>();
    return action;
}
#endif
