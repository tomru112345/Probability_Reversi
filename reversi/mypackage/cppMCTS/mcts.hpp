#ifndef MCTS_HPP
#define MCTS_HPP
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/embed.h>
#include <iostream>
#include "state.hpp"
#include <vector>
#include <tuple>
#include <numeric>
#include <math.h>
#include <algorithm>

using namespace std;
int PV_EVALUATE_COUNT = 12;

tuple<vector<float>, float> predict(pybind11::object model, State state)
{
    auto pypre = pybind11::module::import("pypredict");
    auto res = pypre.attr("predict")(model, state);
    tuple<vector<float>, float> tupleValue = res.cast<tuple<vector<float>, float>>();
    return tupleValue;
}

class Node // モンテカルロ木探索のノードの定義
{
private:
public:
    pybind11::object model;
    State state;
    float p = 0.0;
    float w = 0.0;
    int n = 0;
    vector<Node> child_nodes;

    Node(pybind11::object m, State s, float np) // ノードの初期化
    {
        model = m;
        state = s;
        p = np;
        w = 0.0;
        n = 0;
        vector<Node> child_nodes;
    }

    // vector<float> nodes_to_scores()
    // {
    //     vector<float> scores;
    //     int len_nodes = this->child_nodes.size();
    //     for (int i = 0; i < len_nodes; i++)
    //     {
    //         // cout << this->child_nodes.at(i).n << " ";
    //         scores.push_back(this->child_nodes.at(i).n);
    //     }
    //     // cout << endl;
    //     return scores;
    // }

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
            tuple<vector<float>, float> result = predict(this->model, this->state);
            vector<float> policies = get<0>(result);
            value = get<1>(result);

            // 累計価値と試行回数の更新
            this->w += value;
            this->n += 1;

            // 子ノードの展開
            int len_policies = policies.size();
            for (int i = 0; i < len_policies; i++)
            {
                int action = this->state.legal_actions().at(i);
                State next_state = this->state.next(action);
                float policy = policies.at(i);
                Node next_node = Node(this->model, next_state, policy);
                this->child_nodes.push_back(next_node);
            }
            return value;
        }
        else // 子ノードが存在する時
        {
            // アーク評価値が最大の子ノードの評価で価値を取得
            value = -(next_child_node().evaluate());

            // 累計価値と試行回数の更新
            this->w += value;
            this->n += 1;
            return value;
        }
    }

    Node next_child_node() // アーク評価値が最大の子ノードを取得
    {
        // アーク評価値の計算
        float C_PUCT = 1.0;
        // vector<float> scores = this->nodes_to_scores();
        vector<float> scores = nodes_to_scores(this->child_nodes);
        float t = 0.0;
        for (int i = 0; i < scores.size(); i++)
        {
            t += scores.at(i);
        }
        vector<float> pucb_values;
        int len_child_nodes = this->child_nodes.size();
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
        int argmax_i = *max_element(pucb_values.begin(), pucb_values.end());
        Node next_node = this->child_nodes.at(argmax_i);
        return next_node;
    }
};

vector<float> nodes_to_scores(vector<Node> nodes)
{
    vector<float> scores;
    int len_nodes = nodes.size();
    for (int i = 0; i < len_nodes; i++)
    {
        cout << nodes.at(i).n << " ";
        scores.push_back(nodes.at(i).n);
    }
    cout << endl;
    return scores;
}

vector<float> boltzman(vector<float> xs, float temperature)
{
    float sum_xs = 0;
    int len_xs = xs.size();
    for (int i = 0; i < len_xs; i++)
    {
        float x = xs[i];
        float tmp_n = 1 / temperature;
        xs[i] = pow(x, tmp_n);
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
    Node root_node = Node(model, state, 0);
    vector<float> scores;
    for (int i = 0; i < PV_EVALUATE_COUNT; i++)
    {
        root_node.evaluate();
    }
    // scores = root_node.nodes_to_scores();
    scores = nodes_to_scores(root_node.child_nodes);
    if (temperature == 0.0)
    {
        cout << "a" << endl;
        int action = *max_element(scores.begin(), scores.end());
        scores = vector<float>(scores.size(), 0.0);
        scores[action] = 1;
    }
    else
    {
        cout << "b" << endl;
        scores = boltzman(scores, temperature);
    }
    return scores;
}

int pv_mcts_action(pybind11::object model, State state, float temperature)
{
    vector<int> leg_ac = state.legal_actions();
    for (int i = 0; i < leg_ac.size(); i++)
    {
        cout << leg_ac.at(i) << " ";
    }
    cout << endl;
    vector<float> scores = pv_mcts_scores(model, state, temperature);
    auto pypre = pybind11::module::import("py_rand_choice");
    int action = pypre.attr("choice")(leg_ac, scores).cast<int>();
    return action;
}
#endif
