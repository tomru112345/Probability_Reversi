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
    vector<int> ratio_box;

    int depth = 0;
    vector<vector<int>> dxy = {{1, 0}, {1, 1}, {0, 1}, {-1, 1}, {-1, 0}, {-1, -1}, {0, -1}, {1, -1}};
    bool pass_end = false;
    bool ratio_flg = false;

    State(vector<int> r)
    {
        this->pieces[center_idx - balance_idx - 1] = 1;
        this->pieces[center_idx + balance_idx] = 1;
        this->enemy_pieces[center_idx - balance_idx] = 1;
        this->enemy_pieces[center_idx + balance_idx - 1] = 1;
        this->ratio_box = r;
    }

    State(vector<int> p, vector<int> ep, vector<int> r, int d)
    {
        this->pieces = p;
        this->enemy_pieces = ep;
        this->ratio_box = r;
        this->depth = d;
    }

    void set_ratio(vector<int> r)
    {
        this->ratio_box = r;
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
        State state = static_cast<State>(State(this->pieces, this->enemy_pieces, this->ratio_box, depth + 1));
        if (action != 16)
        {
            int ac_x = action % 4;
            int ac_y = action / 4;
            state.is_legal_action_xy(ac_x, ac_y, true);
        }
        else
        {
            this->ratio_flg = false;
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

    // vector<int> legal_actions();
    // bool is_legal_action_xy_dxy(int x, int y, int dx, int dy, bool flip = false);
    // bool is_legal_action_xy_dxy_penalty(int x, int y, int dx, int dy, bool flip = false);
    // bool is_legal_action_xy(int x, int y, bool flip = false);
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
            if (this->enemy_pieces[x + y * 4] == 1)
            {
                if (flip)
                {
                    for (int i = 0; i < 4; i++)
                    {
                        x -= dx;
                        y -= dy;
                        if (this->enemy_pieces[x + y * 4] == 1)
                        {
                            return true;
                        }
                        this->enemy_pieces[x + y * 4] = 1;
                        this->pieces[x + y * 4] = 0;
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

#endif