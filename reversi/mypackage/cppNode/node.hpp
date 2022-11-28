#ifndef NODE_HPP
#define NODE_HPP

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/embed.h>
#include <vector>
#include <tuple>
#include <random>
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
    State()
    {
        pieces[center_idx - balance_idx - 1] = 1;
        pieces[center_idx + balance_idx] = 1;
        enemy_pieces[center_idx - balance_idx] = 1;
        enemy_pieces[center_idx + balance_idx - 1] = 1;
    }

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

std::tuple<std::vector<double>, double> predict(pybind11::object model, State state)
{
    auto pypre = pybind11::module::import("pypredict");
    auto res = pypre.attr("predict")(model, state);
    std::tuple<std::vector<double>, double> tupleValue = res.cast<std::tuple<std::vector<double>, double>>();
    return tupleValue;
}

// class Node
// {
// private:
//     pybind11::object model;
//     State state;
//     float p = 0.0F;
//     float w = 0.0F;
//     int n = 0;
//     std::vector<Node> child_nodes;

// public:
//     Node()
//     {
//         pybind11::object model;
//         State state;
//         float p = 0.0F;
//         float w = 0.0F;
//         int n = 0;
//         std::vector<Node> child_nodes;
//     }

//     Node(pybind11::object m, State s, float np)
//     {
//         model = m;
//         state = s;
//         p = np;
//         w = 0.0F;
//         n = 0;
//         std::vector<Node> child_nodes;
//     }

//     void set_state(State s)
//     {
//         state = s;
//     }

//     void set_w(float nw)
//     {
//         w = nw;
//     }

//     void set_n(int nn)
//     {
//         n = nn;
//     }

//     void set_child_nodes(std::vector<Node> nc)
//     {
//         child_nodes = nc;
//     }

//     pybind11::object get_model()
//     {
//         return model;
//     }

//     State get_state()
//     {
//         return state;
//     }

//     float get_w()
//     {
//         return w;
//     }

//     int get_n()
//     {
//         return n;
//     }

//     float get_p()
//     {
//         return p;
//     }

//     std::vector<Node> get_child_nodes()
//     {
//         return child_nodes;
//     }

//     void append_new_child(int action, float policy)
//     {
//         std::vector<Node> tmp_cn = get_child_nodes();
//         Node next_node = Node(get_model(), get_state().next(action), policy);
//         tmp_cn.push_back(next_node);
//         set_child_nodes(tmp_cn);
//     }

//     std::vector<int> nodes_to_scores()
//     {
//         std::vector<int> scores;
//         int len_nodes = (int)get_child_nodes().size();
//         for (int i = 0; i < len_nodes; i++)
//         {
//             std::vector<Node> tmp_cn = get_child_nodes();
//             scores.push_back(tmp_cn.at(i).get_n());
//         }
//         return scores;
//     }

//     float evaluate() // 局面の価値の計算
//     {
//         float value = 0.0F;

//         // ゲーム終了時
//         if (get_state().is_done())
//         {
//             // 勝敗結果で価値を取得
//             if (get_state().is_lose())
//             {
//                 value = -1.0F;
//             }
//             else
//             {
//                 value = 0.0F;
//             }

//             // 累計価値と試行回数の更新
//             set_w(get_w() + value);
//             set_n(get_n() + 1);
//             return value;
//         }

//         if (get_child_nodes().empty()) // 子ノードが存在しない時
//         {
//             // ニューラルネットワークの推論で方策と価値を取得
//             std::tuple<std::vector<float>, float> result = predict(get_model(), get_state());
//             std::vector<float> policies = std::get<0>(result);
//             value = std::get<1>(result);

//             // 累計価値と試行回数の更新
//             set_w(get_w() + value);
//             set_n(get_n() + 1);

//             // 子ノードの展開
//             int len_policies = (int)policies.size();
//             for (int i = 0; i < len_policies; i++)
//             {
//                 int action = get_state().legal_actions().at(i);
//                 State next_state = get_state().next(action);
//                 float policy = policies.at(i);
//                 append_new_child(action, policy);
//             }
//             return value;
//         }
//         else // 子ノードが存在する時
//         {
//             // アーク評価値が最大の子ノードの評価で価値を取得
//             int argmax_i = next_child_node_index();
//             std::cout << argmax_i << std::endl;
//             std::vector<Node> tmp_cn = get_child_nodes();
//             value = -(tmp_cn.at(argmax_i).evaluate());

//             // 累計価値と試行回数の更新
//             set_w(get_w() + value);
//             set_n(get_n() + 1);
//             return value;
//         }
//     }

//     int next_child_node_index()
//     {
//         // アーク評価値の計算
//         float C_PUCT = 1.0F;
//         std::vector<int> scores = nodes_to_scores();
//         int t = 0;
//         for (int i = 0; i < scores.size(); i++)
//         {
//             t += scores.at(i);
//         }

//         std::vector<float> pucb_values;
//         int len_child_nodes = (int)get_child_nodes().size();
//         for (int i = 0; i < len_child_nodes; i++)
//         {
//             float tmp_v = 0.0F;
//             if (get_child_nodes().at(i).get_n() != 0.0F)
//             {
//                 tmp_v = -(get_child_nodes().at(i).get_w() / get_child_nodes().at(i).get_n());
//             }
//             else
//             {
//                 tmp_v = 0.0F;
//             }
//             tmp_v += (C_PUCT * get_child_nodes().at(i).get_p() * (float)sqrt(t) / (float)(1 + get_child_nodes().at(i).get_n()));
//             pucb_values.push_back(tmp_v);
//         }
//         // アーク評価値が最大の子ノードを返す
//         int argmax_i = (int)std::distance(pucb_values.begin(), std::max_element(pucb_values.begin(), pucb_values.end()));
//         return argmax_i;
//     }
// };

class Node
{
private:
    pybind11::object model;
    State state;
    double w = 0.0;
    double n = 0.0;
    double p = 0.0;

public:
    std::vector<Node> child_nodes;

    Node()
    {
        pybind11::object model;
        State state;
        double w = 0.0;
        double n = 0.0;
        double p = 0.0;
        std::vector<Node> child_nodes;
    }

    Node(pybind11::object m, State s, double np)
    {
        model = m;
        state = s;
        p = np;
        w = 0.0;
        n = 0.0;
    }

    void set_state(State s)
    {
        state = s;
    }

    void set_w(double nw)
    {
        w = nw;
    }

    void set_n(double nn)
    {
        n = nn;
    }

    State get_state()
    {
        return state;
    }

    pybind11::object get_model()
    {
        return model;
    }

    double get_w()
    {
        return w;
    }

    double get_n()
    {
        return n;
    }

    double get_p()
    {
        return p;
    }

    void append_new_child(int action, double policy)
    {
        Node next_node = Node(get_model(), get_state().next(action), policy);
        this->child_nodes.push_back(next_node);
    }

    std::vector<double> nodes_to_scores()
    {
        std::vector<double> scores;
        int len_nodes = (int)this->child_nodes.size();
        for (int i = 0; i < len_nodes; i++)
        {
            scores.push_back(this->child_nodes.at(i).get_n());
        }
        return scores;
    }

    double evaluate() // 局面の価値の計算
    {
        double value = 0.0;

        // ゲーム終了時
        if (get_state().is_done())
        {
            // 勝敗結果で価値を取得
            if (get_state().is_lose())
            {
                value = -1.0;
            }
            else
            {
                value = 0.0;
            }

            // 累計価値と試行回数の更新
            set_w(get_w() + value);
            set_n(get_n() + 1.0);
            return value;
        }

        if (this->child_nodes.empty()) // 子ノードが存在しない時
        {
            // ニューラルネットワークの推論で方策と価値を取得
            std::tuple<std::vector<double>, double> result = predict(get_model(), get_state());
            std::vector<double> policies = std::get<0>(result);
            value = std::get<1>(result);

            // 累計価値と試行回数の更新
            set_w(get_w() + value);
            set_n(get_n() + 1.0);

            // 子ノードの展開
            int len_policies = (int)policies.size();
            for (int i = 0; i < len_policies; i++)
            {
                int action = get_state().legal_actions().at(i);
                State next_state = get_state().next(action);
                double policy = policies.at(i);
                append_new_child(action, policy);
            }
            return value;
        }
        else // 子ノードが存在する時
        {
            // アーク評価値が最大の子ノードの評価で価値を取得
            int argmax_i = next_child_node_index();
            value = -(this->child_nodes.at(argmax_i).evaluate());

            // 累計価値と試行回数の更新
            set_w(get_w() + value);
            set_n(get_n() + 1.0);
            return value;
        }
    }

    int next_child_node_index()
    {
        // アーク評価値の計算
        double C_PUCT = 1.0;
        std::vector<double> scores = nodes_to_scores();
        double t = 0.0;
        for (int i = 0; i < scores.size(); i++)
        {
            t += scores.at(i);
        }

        std::vector<double> pucb_values;
        int len_child_nodes = (int)this->child_nodes.size();
        for (int i = 0; i < len_child_nodes; i++)
        {
            double tmp_v = 0.0;
            if (this->child_nodes.at(i).get_n() != 0.0)
            {
                tmp_v = -(this->child_nodes.at(i).get_w() / this->child_nodes.at(i).get_n());
            }
            else
            {
                tmp_v = 0.0;
            }
            tmp_v += (C_PUCT * this->child_nodes.at(i).get_p() * (double)sqrt(t) / (1.0F + this->child_nodes.at(i).get_n()));
            pucb_values.push_back(tmp_v);
        }
        // アーク評価値が最大の子ノードを返す
        int argmax_i = (int)std::distance(pucb_values.begin(), std::max_element(pucb_values.begin(), pucb_values.end()));
        return argmax_i;
    }
};

std::vector<double> boltzman(std::vector<double> xs, double temperature)
{
    double sum_xs = 0.0;
    int len_xs = (int)xs.size();
    for (int i = 0; i < len_xs; i++)
    {
        double x = xs[i];
        double tmp_n = 1 / temperature;
        xs[i] = (double)pow(x, tmp_n);
        sum_xs += xs[i];
    }
    std::vector<double> new_xs(len_xs, 0.0);
    for (int i = 0; i < len_xs; i++)
    {
        new_xs[i] = xs[i] / sum_xs;
    }
    return new_xs;
}

std::vector<double> pv_mcts_scores(pybind11::object model, State state, double temperature)
{

    Node root_node = Node(model, state, 0);
    std::vector<double> scores;
    for (int i = 0; i < PV_EVALUATE_COUNT; i++)
    {
        root_node.evaluate();
    }

    scores = root_node.nodes_to_scores();
    if (temperature == 0.0)
    {
        int action = (int)std::distance(scores.begin(), std::max_element(scores.begin(), scores.end()));
        scores = std::vector<double>(scores.size(), 0.0);
        scores[action] = 1;
    }
    else
    {
        scores = boltzman(scores, temperature);
    }
    return scores;
}

int pv_mcts_action(pybind11::object model, State state, double temperature)
{
    std::random_device seed_gen;
    std::mt19937 engine(seed_gen());
    std::vector<int> leg_ac = state.legal_actions();
    std::vector<double> scores = pv_mcts_scores(model, state, temperature);
    std::discrete_distribution<std::size_t> dist(scores.begin(), scores.end());
    int result_index = (int)dist(engine);
    int action = leg_ac.at(result_index);
    return action;
}

#endif