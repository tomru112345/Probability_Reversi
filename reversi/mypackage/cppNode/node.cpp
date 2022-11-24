#include "node.hpp"



float evaluate(Node node) // 局面の価値の計算
{
    float value = 0.0;

    // ゲーム終了時
    if (node.state.is_done())
    {
        // 勝敗結果で価値を取得
        if (node.state.is_lose())
        {
            value = -1.0;
        }
        else
        {
            value = 0.0;
        }

        // 累計価値と試行回数の更新
        node.w += value;
        node.n += 1.0;
        return value;
    }

    if (node.child_nodes.empty()) // 子ノードが存在しない時
    {
        // ニューラルネットワークの推論で方策と価値を取得
        std::tuple<std::vector<float>, float> result = predict(node.model, node.state);
        std::vector<float> policies = std::get<0>(result);
        value = std::get<1>(result);

        // 累計価値と試行回数の更新
        node.w += value;
        node.n += 1.0;

        // 子ノードの展開
        int len_policies = policies.size();
        for (int i = 0; i < len_policies; i++)
        {
            int action = node.state.legal_actions().at(i);
            State next_state = node.state.next(action);
            float policy = policies.at(i);
            Node next_node = Node(node.model, next_state, policy);
            node.child_nodes.push_back(next_node);
        }
        return value;
    }
    else // 子ノードが存在する時
    {
        // アーク評価値が最大の子ノードの評価で価値を取得
        // value = -(next_child_node().evaluate());
        value = -(evaluate(next_child_node(node)));

        // 累計価値と試行回数の更新
        node.w += value;
        node.n += 1.0;
        return value;
    }
}



// Node Node::next_child_node() // アーク評価値が最大の子ノードを取得
// {
//     // アーク評価値の計算
//     float C_PUCT = 1.0;
//     // vector<float> scores = this->nodes_to_scores();
//     std::vector<float> scores = nodes_to_scores(this->child_nodes);
//     float t = 0.0;
//     for (int i = 0; i < scores.size(); i++)
//     {
//         t += scores.at(i);
//     }
//     std::vector<float> pucb_values;
//     int len_child_nodes = this->child_nodes.size();
//     for (int i = 0; i < len_child_nodes; i++)
//     {
//         float tmp_v = 0.0;
//         if (this->child_nodes.at(i).n != 0.0)
//         {
//             tmp_v = -(this->child_nodes.at(i).w / this->child_nodes.at(i).n);
//         }
//         else
//         {
//             tmp_v = 0.0;
//         }
//         tmp_v += (C_PUCT * this->child_nodes.at(i).p * sqrt(t) / (1 + this->child_nodes.at(i).n));
//         pucb_values.push_back(tmp_v);
//     }

//     // アーク評価値が最大の子ノードを返す
//     int argmax_i = *std::max_element(pucb_values.begin(), pucb_values.end());
//     Node next_node = this->child_nodes.at(argmax_i);
//     return next_node;
// }