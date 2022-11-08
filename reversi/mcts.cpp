#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
using namespace std;
namespace py = pybind11;

// #include <Eigen/Dense>
// #include <pybind11/eigen.h>

// namespace py = pybind11;
// Eigen::MatrixXd m(2, 2);

// Eigen::MartixXd reshape(int a, int b, int c)
// {
// }

class MCTS
{
private:
public:
    float temperature = 0;
    MCTS(float temperature)
    {
        this->temperature = temperature;
    }

    vector<float> boltzman(vector<float> xs)
    {
        int len_xs = xs.size();
        float sum_xs = 0;
        for (int i = 0; i < len_xs; i++)
        {
            float x = xs[i];
            xs[i] = pow(x, 1 / temperature);
            sum_xs += xs[i];
        }
        vector<float> new_xs(len_xs);
        for (int i = 0; i < len_xs; i++)
        {
            new_xs[i] = 0.0;
            new_xs[i] = xs[i] / sum_xs;
        }
        return new_xs;
    }
};

PYBIND11_PLUGIN(cppMCTS)
{
    py::module m("cppMCTS", "pybind11 example plugin");
    py::class_<MCTS>(m, "MCTS")
        .def(py::init<float>())
        .def("boltzman", &MCTS::boltzman);
    return m.ptr();
}
