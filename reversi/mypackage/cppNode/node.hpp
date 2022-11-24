#ifndef NODE_HPP
#define NODE_HPP

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/embed.h>
#include <vector>
#include <tuple>
#include <numeric>
#include <math.h>
#include <algorithm>
#include <iostream>

int PV_EVALUATE_COUNT = 12;

class State
{
private:
    static const int center_idx = 8;
    static const int balance_idx = 2;
    std::vector<int> pieces = std::vector<int>(16, 0);
    std::vector<int> enemy_pieces = std::vector<int>(16, 0);
    std::vector<int> ratio_box;
    int depth = 0;
    std::vector<std::vector<int>> dxy = {{1, 0}, {1, 1}, {0, 1}, {-1, 1}, {-1, 0}, {-1, -1}, {0, -1}, {1, -1}};
    bool pass_end = false;

public:
    State(std::vector<int> r)
    {
        pieces[center_idx - balance_idx - 1] = 1;
        pieces[center_idx + balance_idx] = 1;
        enemy_pieces[center_idx - balance_idx] = 1;
        enemy_pieces[center_idx + balance_idx - 1] = 1;
        ratio_box = r;
    }

    State(std::vector<int> p, std::vector<int> ep, std::vector<int> r, int d)
    {
        pieces = p;
        enemy_pieces = ep;
        ratio_box = r;
        depth = d;
    }

    void set_pieces(std::vector<int> p)
    {
        pieces = p;
    }

    void set_enemy_pieces(std::vector<int> ep)
    {
        enemy_pieces = ep;
    }

    void set_ratio_box(std::vector<int> r)
    {
        ratio_box = r;
    }

    void set_depth(int d)
    {
        depth = d;
    }

    void set_pass_end(bool pe)
    {
        pass_end = pe;
    }

    std::vector<int> get_pieces()
    {
        return pieces;
    }

    std::vector<int> get_enemy_pieces()
    {
        return enemy_pieces;
    }

    std::vector<int> get_ratio_box()
    {
        return ratio_box;
    }

    int get_depth()
    {
        return depth;
    }

    bool get_pass_end()
    {
        return pass_end;
    }

    std::vector<std::vector<int>> get_dxy()
    {
        return dxy;
    }

    int piece_count(std::vector<int> p)
    {
        int cnt = 0;
        for (int i = 0; i < p.size(); i++)
        {
            if (p[i] == 1)
            {
                cnt++;
            }
        }
        return cnt;
    }

    bool is_done()
    {
        if ((piece_count(get_pieces()) + piece_count(get_enemy_pieces()) == 16) || get_pass_end())
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
        if (is_done() && (piece_count(get_pieces()) < piece_count(get_enemy_pieces())))
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
        if (is_done() && (piece_count(get_pieces()) == piece_count(get_enemy_pieces())))
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
        return (get_depth() % 2 == 0);
    }

    State next(int action)
    {
        State state = State(get_pieces(), get_enemy_pieces(), get_ratio_box(), get_depth() + 1);
        if (action != 16)
        {
            int ac_x = action % 4;
            int ac_y = action / 4;
            state.is_legal_action_xy(ac_x, ac_y, true);
        }

        std::vector<int> w = state.get_pieces();
        state.set_pieces(state.get_enemy_pieces());
        state.set_enemy_pieces(w);

        std::vector<int> pass_vec = {16};
        std::vector<int> leg_vec = state.legal_actions();
        if (action == 16 && leg_vec == pass_vec)
        {
            state.set_pass_end(true);
        }
        return state;
    }

    // vector<int> legal_actions();
    // bool is_legal_action_xy_dxy(int x, int y, int dx, int dy, bool flip = false);
    // bool is_legal_action_xy_dxy_penalty(int x, int y, int dx, int dy, bool flip = false);
    // bool is_legal_action_xy(int x, int y, bool flip = false);

    std::vector<int> legal_actions()
    {
        std::vector<int> actions;
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
        else if (get_enemy_pieces()[new_x + new_y * 4] != 1)
        {
            return false;
        }

        for (int j = 0; j < 4; j++)
        {
            if ((new_y < 0) || (3 < new_y) || (new_x < 0) || (3 < new_x))
            {
                return false;
            }
            else if (get_enemy_pieces()[new_x + new_y * 4] == 0 && get_pieces()[new_x + new_y * 4] == 0)
            {
                return false;
            }
            if (get_pieces()[new_x + new_y * 4] == 1)
            {
                if (flip)
                {
                    for (int i = 0; i < 4; i++)
                    {
                        new_x -= dx;
                        new_y -= dy;
                        if (get_pieces()[new_x + new_y * 4] == 1)
                        {
                            return true;
                        }
                        std::vector<int> tmp_p = get_pieces();
                        tmp_p[new_x + new_y * 4] = 1;
                        set_pieces(tmp_p);
                        std::vector<int> tmp_ep = get_enemy_pieces();
                        tmp_ep[new_x + new_y * 4] = 0;
                        set_enemy_pieces(tmp_ep);
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
        if ((y < 0) || (3 < y) || (x < 0) || (3 < x) || (get_enemy_pieces()[x + y * 4] != 1))
        {
            return false;
        }

        for (int j = 0; j < 4; j++)
        {
            if ((y < 0) || (3 < y) || (x < 0) || (3 < x) || ((get_enemy_pieces()[x + y * 4] == 0) && (get_pieces()[x + y * 4] == 0)))
            {
                return false;
            }
            if (get_enemy_pieces()[x + y * 4] == 1)
            {
                if (flip)
                {
                    for (int i = 0; i < 4; i++)
                    {
                        x -= dx;
                        y -= dy;
                        if (get_enemy_pieces()[x + y * 4] == 1)
                        {
                            return true;
                        }
                        std::vector<int> tmp_ep = get_enemy_pieces();
                        tmp_ep[x + y * 4] = 1;
                        set_enemy_pieces(tmp_ep);
                        std::vector<int> tmp_p = get_pieces();
                        tmp_p[x + y * 4] = 0;
                        set_pieces(tmp_p);
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
        if (get_enemy_pieces()[x + y * 4] == 1 || get_pieces()[x + y * 4] == 1)
        {
            return false;
        }
        if (flip)
        {
            if (rand() % 101 <= get_ratio_box()[x + y * 4])
            {
                std::vector<int> tmp_p = get_pieces();
                tmp_p[x + y * 4] = 1;
                set_pieces(tmp_p);
            }
            else
            {
                std::vector<int> tmp_ep = get_enemy_pieces();
                tmp_ep[x + y * 4] = 1;
                set_enemy_pieces(tmp_ep);
                for (int i = 0; i < get_dxy().size(); i++)
                {
                    is_legal_action_xy_dxy_penalty(x, y, get_dxy()[i][0], get_dxy()[i][1], flip);
                }
                return false;
            }
        }
        bool flag = false;
        for (int i = 0; i < get_dxy().size(); i++)
        {
            if (is_legal_action_xy_dxy(x, y, get_dxy()[i][0], get_dxy()[i][1], flip))
            {
                flag = true;
            }
        }
        return flag;
    }
};

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
    float n = 0.0;
    std::vector<Node> child_nodes;

    Node(pybind11::object m, State s, float np) // ノードの初期化
    {
        model = m;
        state = s;
        p = np;
        w = 0.0;
        n = 0.0;
    }

    void append_new_child(int action, float policy)
    {
        Node next_node = Node(this->model, this->state.next(action), policy);
        this->child_nodes.push_back(next_node);
    }

    std::vector<float> nodes_to_scores()
    {
        std::vector<float> scores;
        int len_nodes = (int)this->child_nodes.size();
        for (int i = 0; i < len_nodes; i++)
        {
            scores.push_back(this->child_nodes.at(i).n);
        }
        return scores;
    }

    float evaluate() // 局面の価値の計算
    {
        float value = 0.0;

        // ゲーム終了時
        if (this->state.is_done())
        {
            // 勝敗結果で価値を取得
            if (this->state.is_lose())
            {
                value = -1.0;
            }
            else
            {
                value = 0.0;
            }

            // 累計価値と試行回数の更新
            this->w += value;
            this->n += 1;
            return value;
        }

        if (this->child_nodes.empty()) // 子ノードが存在しない時
        {
            // ニューラルネットワークの推論で方策と価値を取得
            std::tuple<std::vector<float>, float> result = predict(this->model, this->state);
            std::vector<float> policies = std::get<0>(result);
            value = std::get<1>(result);

            // 累計価値と試行回数の更新
            this->w += value;
            this->n += 1;

            // 子ノードの展開
            int len_policies = (int)policies.size();
            for (int i = 0; i < len_policies; i++)
            {
                int action = this->state.legal_actions().at(i);
                State next_state = this->state.next(action);
                float policy = policies.at(i);
                append_new_child(action, policy);
            }
            return value;
        }
        else // 子ノードが存在する時
        {
            // アーク評価値が最大の子ノードの評価で価値を取得
            int argmax_i = next_child_node_index();
            value = -(this->child_nodes[argmax_i].evaluate());

            // 累計価値と試行回数の更新
            this->w += value;
            this->n += 1;
            return value;
        }
    }

    int next_child_node_index()
    {
        // アーク評価値の計算
        float C_PUCT = 1.0;
        std::vector<float> scores = this->nodes_to_scores();
        float t = 0.0;
        for (int i = 0; i < scores.size(); i++)
        {
            t += scores.at(i);
        }

        std::vector<float> pucb_values;
        int len_child_nodes = (int)this->child_nodes.size();
        for (int i = 0; i < len_child_nodes; i++)
        {
            float tmp_v = 0.0;
            if (this->child_nodes.at(i).n != 0.0)
            {
                tmp_v = -(this->child_nodes.at(i).w / this->child_nodes.at(i).n);
            }
            else
            {
                tmp_v = 0.0;
            }
            tmp_v += (C_PUCT * this->child_nodes.at(i).p * sqrt(t) / (1 + this->child_nodes.at(i).n));
            pucb_values.push_back(tmp_v);
        }
        // アーク評価値が最大の子ノードを返す
        int argmax_i = (int)std::distance(pucb_values.begin(), std::max_element(pucb_values.begin(), pucb_values.end()));
        return argmax_i;
    }
};

#endif