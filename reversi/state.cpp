#include "state.hpp"
#include <iostream>
#include <cstdlib>
#include <algorithm>

using namespace std;

vector<int> State::legal_actions()
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

bool State::is_legal_action_xy_dxy(int x, int y, int dx, int dy, bool flip = false)
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

bool State::is_legal_action_xy_dxy_penalty(int x, int y, int dx, int dy, bool flip = false)
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

bool State::is_legal_action_xy(int x, int y, bool flip = false)
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
