#ifndef VEAP_RL_POLICY_H
#define VEAP_RL_POLICY_H
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Values in action order: north, east, south, west. */
int veap_greedy(const double values[4]);
double veap_q_update(double current, double reward, const double next[4],
                     int terminal, double alpha, double discount);
#ifdef __cplusplus
}
#endif
#endif
