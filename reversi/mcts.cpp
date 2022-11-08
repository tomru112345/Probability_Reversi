#include <pybind11/pybind11.h>
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
        this.temperature = temperature;
    }

    float *boltzman(float xs[])
    {
        int len_xs = sizeof(xs) / sizeof(xs[0]);
        float sum_xs = 0;
        for (int i = 0; i < len_xs; i++)
        {
            float x = xs[i];
            xs[i] = std::pow(x, 1 / temperature);
            sum_xs += xs[i];
        }
        float new_xs[len_xs];
        for (int i = 0; i < len_xs; i++)
        {
            new_xs[i] = 0.0;
            new_xs[i] = xs[i] / sum_xs;
        }
        return new_xs;
    }
}

PYBIND11_MODULE(mcts, m)
{
    pybind11::class_<MCTS>(m, "MCTS").def("boltzman", &MCTS::boltzman);
    // m.def("MCTS", &MCTS);
}