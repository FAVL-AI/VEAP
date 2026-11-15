#include "policy.h"

int veap_greedy(const double values[4]) {
    int best = 0;
    for (int i = 1; i < 4; ++i)
        if (values[i] > values[best]) best = i;
    return best;
}

double veap_q_update(double current, double reward, const double next[4],
                     int terminal, double alpha, double discount) {
    double target = reward;
    if (!terminal) target += discount * next[veap_greedy(next)];
    return current + alpha * (target - current);
}
