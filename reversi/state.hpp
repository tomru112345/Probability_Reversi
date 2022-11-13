#ifndef   STATE_HPP
#define   STATE_HPP
#include <vector>
using namespace std;

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

    State();
    State(vector<int> p, vector<int> ep, vector<int> r, int d);
    int piece_count(vector<int> pieces);
    bool is_done();
    bool is_lose();
    bool is_draw();
    State next(int action);
    vector<int> legal_actions();
    bool is_legal_action_xy_dxy(int x, int y, int dx, int dy, bool flip = false);
    bool is_legal_action_xy_dxy_penalty(int x, int y, int dx, int dy, bool flip = false);
    bool is_legal_action_xy(int x, int y, bool flip = false);
    bool is_first_player();
};

#endif // STATE_HPP