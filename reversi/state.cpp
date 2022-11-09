#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <iostream>
#include <vector>
#include <cstdlib>
using namespace std;
namespace py = pybind11;

class State
{
private:
public:
    vector<int> pieces;
    vector<int> enemy_pieces;
    vector<int> ratio_box;
    static const int center_idx = 8;
    static const int balance_idx = 2;
    int depth = 0;
    vector<vector<int>> dxy = {{1, 0}, {1, 1}, {0, 1}, {-1, 1}, {-1, 0}, {-1, -1}, {0, -1}, {1, -1}};
    bool pass_end = false;
    
    State()
    {
        pieces = vector<int>(16, 0);
        enemy_pieces = vector<int>(16, 0);
        ratio_box = vector<int>(16, 100);
        pieces[center_idx - balance_idx - 1] = 1;
        pieces[center_idx + balance_idx] = 1;
        enemy_pieces[center_idx - balance_idx] = 1;
        enemy_pieces[center_idx + balance_idx - 1] = 1;
    }

    State(vector<int> p, vector<int> ep, vector<int> r, int d)
    {
        pieces = p;
        enemy_pieces = ep;
        ratio_box = r;
        depth = d;
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
        if ((piece_count(pieces) + piece_count(enemy_pieces) == 16) || pass_end)
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
        if (is_done() && (piece_count(pieces) < piece_count(enemy_pieces)))
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
        if (is_done() && (piece_count(pieces) == piece_count(enemy_pieces)))
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
         State state = State(pieces, enemy_pieces, ratio_box, depth + 1);
         vector<int> pass_vec = {16};
         if (action != 16){
             int ac_x = action % 4;
             int ac_y = action / 4;
             state.is_legal_action_xy(ac_x, ac_y, true);
         }

         vector<int> w = state.pieces;
         state.pieces = state.enemy_pieces;
         state.enemy_pieces = w;

         if (action == 16 && state.legal_actions() == pass_vec)
         {
             pass_end = true;
    
    	 }
         return state;
     }

    //void next(int action)
    //{
    //    depth++;
    //    vector<int> pass_vec = {16};
    //    if (action != 16)
    //    {
            //int ac_x = action % 4;
            //int ac_y = action / 4;
          //  is_legal_action_xy(ac_x, ac_y, true);
        //}

        //vector<int> w = pieces;
       // pieces = enemy_pieces;
       // enemy_pieces = w;

       // if (action == 16 && legal_actions() == pass_vec)
      //  {
       //     pass_end = true;
     //   }
    //}

    vector<int> legal_actions()
    {
        vector<int> actions;
        for (int j = 0; j < 4; j++)
        {
            for (int i = 0; i < 4; i++)
            {
                if (is_legal_action_xy(i, j))
                {
                    int val = i + j * 4;
                    actions.push_back(val);
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
        x += dx;
        y += dy;
        if ((y < 0) || (3 < y) || (x < 0) || (3 < x) || ((enemy_pieces[x + y * 4]) != 1))
        {
            return false;
        }

        for (int j = 0; j < 4; j++)
        {
            if ((y < 0) || (3 < y) || (x < 0) || (3 < x) || (enemy_pieces[x + y * 4] == 0 && pieces[x + y * 4] == 0))
            {
                return false;
            }
            if (pieces[x + y * 4] == 1)
            {
                if (flip)
                {
                    for (int i = 0; i < 3; i++)
                    {
                        x -= dx;
                        y -= dy;
                        if (pieces[x + y * 4] == 1)
                        {
                            return true;
                        }
                        pieces[x + y * 4] = 1;
                        enemy_pieces[x + y * 4] = 0;
                    }
                    return true;
                }
                x += dx;
                y += dy;
            }
        }
        return false;
    }

    bool is_legal_action_xy_dxy_penalty(int x, int y, int dx, int dy, bool flip = false)
    {
        x += dx;
        y += dy;
        if ((y < 0) || (3 < y) || (x < 0) || (3 < x) || ((enemy_pieces[x + y * 4]) != 1))
        {
            return false;
        }

        for (int j = 0; j < 4; j++)
        {
            if ((y < 0) || (3 < y) || (x < 0) || (3 < x) || (((enemy_pieces[x + y * 4]) == 0) && ((pieces[x + y * 4]) == 0)))
            {
                return false;
            }
            if (pieces[x + y * 4] == 1)
            {
                if (flip)
                {
                    for (int i = 0; i < 3; i++)
                    {
                        x -= dx;
                        y -= dy;
                        if (pieces[x + y * 4] == 1)
                        {
                            return true;
                        }
                        pieces[x + y * 4] = 1;
                        enemy_pieces[x + y * 4] = 0;
                    }
                    return true;
                }
                x += dx;
                y += dy;
            }
        }
        return false;
    }

    bool is_legal_action_xy(int x, int y, bool flip = false)
    {
        if (enemy_pieces[x + y * 4] == 1 || pieces[x + y * 4] == 1)
        {
            return false;
        }
        if (flip)
        {
            if (rand() % 101 <= ratio_box[x + y * 4])
            {
                pieces[x + y * 4] = 1;
            }
            else
            {
                enemy_pieces[x + y * 4] = 1;
                for (int i = 0; i < dxy.size(); i++)
                {
                    is_legal_action_xy_dxy_penalty(x, y, dxy[i][0], dxy[i][1], flip);
                }
                return false;
            }
        }
        bool flag = false;
        for (int i = 0; i < dxy.size(); i++)
        {
            if (is_legal_action_xy_dxy(x, y, dxy[i][0], dxy[i][1], flip))
            {
                flag = true;
            }
        }
        return flag;
    }

    bool
    is_first_player()
    {
        return (depth % 2 == 0);
    }
};

int main()
{
    State state = State();
    cout << state.is_first_player() << endl;
}

PYBIND11_MODULE(cppState, m)
{
    py::class_<State>(m, "State")
        .def(py::init())
        .def(py::init<vector<int>, vector<int>, vector<int>, int>())
	.def_readwrite("pieces", &State::pieces)
	.def_readwrite("enemy_pieces", &State::enemy_pieces)
	.def_readwrite("ratio_box", &State::ratio_box)
	.def_readwrite("depth", &State::depth)
	.def_readwrite("dxy", &State::dxy)
	.def_readwrite("pass_end", &State::pass_end)
        .def("piece_count", &State::piece_count)
        .def("is_done", &State::is_done)
        .def("is_lose", &State::is_lose)
        .def("is_draw", &State::is_draw)
        .def("next", &State::next)
        .def("legal_actions", &State::legal_actions)
        .def("is_legal_action_xy_dxy", &State::is_legal_action_xy_dxy)
        .def("is_legal_action_xy_dxy_penalty", &State::is_legal_action_xy_dxy_penalty)
        .def("is_legal_action_xy", &State::is_legal_action_xy)
        .def("is_first_player", &State::is_first_player);
}
