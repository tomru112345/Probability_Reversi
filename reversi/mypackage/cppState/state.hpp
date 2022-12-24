#ifndef STATE_HPP
#define STATE_HPP
#include <vector>

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

    State next(int action, float set_ratio)
    {
        State state = State(get_pieces(), get_enemy_pieces(), get_ratio_box(), get_depth() + 1);
        if (action != 16)
        {
            int ac_x = action % 4;
            int ac_y = action / 4;
            if (set_ratio * 100 < ratio_box[ac_x + ac_y * 4])
            {
                state.is_legal_action_xy(ac_x, ac_y, true, true);
            }
            else
            {
                state.is_legal_action_xy(ac_x, ac_y, true, false);
            }
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

    bool is_legal_action_xy(int x, int y, bool flip = false, bool success_flg = true)
    {
        if (get_enemy_pieces()[x + y * 4] == 1 || get_pieces()[x + y * 4] == 1)
        {
            return false;
        }
        if (flip)
        {
            // if (rand() % 101 <= get_ratio_box()[x + y * 4])
            if (success_flg)
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

#endif