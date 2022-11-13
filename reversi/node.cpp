#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/embed.h>
#include "keras_model.h"
#include <vector>
#include <tuple>
#include <numeric>
#include <math.h>
#include <algorithm>
#include <stdio.h>
#include <stdlib.h>

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

    bool is_first_player()
    {
        return (this->depth % 2 == 0);
    }
};

struct result_t
{
    vector<int> p;
    int v;
};

struct result_t predict(KerasModel model, State state)
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
    KerasModel model;
    State state;
    int p = 0;
    int w = 0;
    int n = 0;
    vector<Node> child_nodes;

public:
    Node(KerasModel m, State s, int np)
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
            int argmax_i = *max_element(pucb_values.begin(), pucb_values.end());
            return this->child_nodes.at(argmax_i);
        }
    }
};