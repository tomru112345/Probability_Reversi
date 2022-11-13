#ifndef STATE_HPP
#define STATE_HPP
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

    State next(int action);
    vector<int> legal_actions();
    bool is_legal_action_xy_dxy(int x, int y, int dx, int dy, bool flip = false);
    bool is_legal_action_xy_dxy_penalty(int x, int y, int dx, int dy, bool flip = false);
    bool is_legal_action_xy(int x, int y, bool flip = false);
};

#endif // STATE_HPP