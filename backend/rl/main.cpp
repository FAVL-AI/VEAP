#include "policy.h"
#include "physics_env.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <unistd.h>
#include <vector>

using Row = std::array<double, 4>;
using Policy = std::array<Row, 36>;
using PhysPolicy = std::array<Row, 117>;

// Versioned synthetic navigation environment. Coordinates are row-major.
constexpr std::array<const char*, 6> map = {"......", ".###..", "...#..", ".#....", ".#.#..", ".....G"};
constexpr int goal = 35;

bool blocked(int s) { return map[s / 6][s % 6] == '#'; }

int move_agent(int s, int a) {
    constexpr int dx[] = {0, 1, 0, -1}, dy[] = {-1, 0, 1, 0};
    int x = s % 6 + dx[a], y = s / 6 + dy[a];
    if (x < 0 || y < 0 || x >= 6 || y >= 6 || blocked(y * 6 + x)) return s;
    return y * 6 + x;
}

void save(const Policy& policy, const std::string& path) {
    std::string temporary = path + ".tmp.XXXXXX";
    int fd = mkstemp(temporary.data());
    if (fd < 0) throw std::runtime_error("cannot create checkpoint");
    FILE* out = fdopen(fd, "w");
    if (!out) {
        close(fd);
        std::remove(temporary.c_str());
        throw std::runtime_error("cannot open checkpoint");
    }
    bool ok = std::fprintf(out, "VEAP-Q1 grid6-v1 36 4\n") > 0;
    for (const auto& row : policy) {
        for (double value : row)
            if (std::fprintf(out, "%.17g ", value) < 0) ok = false;
        if (std::fputc('\n', out) == EOF) ok = false;
    }
    if (std::fclose(out) != 0) ok = false;
    if (!ok || std::rename(temporary.c_str(), path.c_str()) != 0) {
        std::remove(temporary.c_str());
        throw std::runtime_error("checkpoint write failed");
    }
}

Policy load(const std::string& path) {
    std::ifstream in(path);
    std::string header, extra;
    std::getline(in, header);
    if (header != "VEAP-Q1 grid6-v1 36 4") throw std::runtime_error("invalid checkpoint header");
    Policy policy{};
    for (auto& row : policy)
        for (double& value : row)
            if (!(in >> value) || !std::isfinite(value)) throw std::runtime_error("invalid checkpoint value");
    if (in >> extra) throw std::runtime_error("unexpected checkpoint data");
    return policy;
}

void train(Policy& policy, unsigned seed) {
    std::mt19937 rng(seed);
    std::uniform_int_distribution<int> start(0, 34), action(0, 3);
    std::bernoulli_distribution explore(0.25);
    for (int episode = 0; episode < 5000; ++episode) {
        int s;
        do { s = start(rng); } while (blocked(s));
        for (int step = 0; step < 80 && s != goal; ++step) {
            int a = explore(rng) ? action(rng) : veap_greedy(policy[s].data());
            int next = move_agent(s, a);
            double reward = next == goal ? 10.0 : (next == s ? -2.0 : -0.1);
            policy[s][a] = veap_q_update(policy[s][a], reward, policy[next].data(), next == goal, 0.2, 0.95);
            s = next;
        }
    }
}

int evaluate(const Policy& policy) {
    int successes = 0, starts = 0, transitions = 0;
    for (int s = 0; s < goal; ++s) {
        if (blocked(s)) continue;
        ++starts;
        int pos = s;
        for (int t = 0; t < 80 && pos != goal; ++t) {
            pos = move_agent(pos, veap_greedy(policy[pos].data()));
            ++transitions;
        }
        successes += pos == goal;
    }
    std::cout << "{\"starts\":" << starts << ",\"successes\":" << successes
              << ",\"transitions\":" << transitions << "}\n";
    return successes == starts ? 0 : 1;
}

// ----------------- Physics RL Learner Extensions -----------------

inline int quantize_state(double x, double y) {
    int gx = std::clamp(static_cast<int>(x), 0, 12);
    int gy = std::clamp(static_cast<int>(y), 0, 8);
    return gy * 13 + gx;
}

void save_phys(const PhysPolicy& policy, const std::string& path) {
    std::ofstream out(path);
    if (!out.is_open()) throw std::runtime_error("cannot create physics checkpoint");
    out << "VEAP-Q-PHYS warehouse-v1 117 4\n";
    for (const auto& row : policy) {
        for (double val : row) {
            out << std::setprecision(17) << val << ' ';
        }
        out << '\n';
    }
}

PhysPolicy load_phys(const std::string& path) {
    std::ifstream in(path);
    std::string header;
    std::getline(in, header);
    if (header != "VEAP-Q-PHYS warehouse-v1 117 4") {
        throw std::runtime_error("invalid physics checkpoint header");
    }
    PhysPolicy policy{};
    for (auto& row : policy) {
        for (double& val : row) {
            if (!(in >> val) || !std::isfinite(val)) {
                throw std::runtime_error("invalid physics checkpoint value");
            }
        }
    }
    return policy;
}

void train_physics(PhysPolicy& policy, unsigned seed, int episodes) {
    std::mt19937 rng(seed);
    std::uniform_int_distribution<int> action_dist(0, 3);
    std::bernoulli_distribution explore(0.20);
    veap::PhysicsEnv env;

    for (int ep = 0; ep < episodes; ++ep) {
        auto step_res = env.reset(1.2, 1.3, 0.0);
        int s = quantize_state(step_res.observation.x, step_res.observation.y);

        for (int st = 0; st < 120; ++st) {
            int a = explore(rng) ? action_dist(rng) : veap_greedy(policy[s].data());
            auto next_res = env.step_discrete(a);
            int s_next = quantize_state(next_res.observation.x, next_res.observation.y);

            policy[s][a] = veap_q_update(
                policy[s][a],
                next_res.reward,
                policy[s_next].data(),
                next_res.terminated ? 1 : 0,
                0.15,
                0.95
            );

            s = s_next;
            if (next_res.terminated || next_res.truncated) break;
        }
    }
}

int evaluate_physics(const PhysPolicy& policy) {
    veap::PhysicsEnv env;
    auto step_res = env.reset(1.2, 1.3, 0.0);
    int s = quantize_state(step_res.observation.x, step_res.observation.y);
    int steps = 0;
    double total_reward = 0.0;

    for (; steps < 150; ++steps) {
        int a = veap_greedy(policy[s].data());
        auto next_res = env.step_discrete(a);
        s = quantize_state(next_res.observation.x, next_res.observation.y);
        total_reward = next_res.cumulative_reward;
        if (next_res.terminated || next_res.truncated) {
            step_res = next_res;
            break;
        }
        step_res = next_res;
    }

    std::cout << "{\"evaluation\": \"physics_policy\", \"steps\": " << steps
              << ", \"final_x\": " << step_res.observation.x
              << ", \"final_y\": " << step_res.observation.y
              << ", \"dist_to_target\": " << step_res.observation.dist_to_target
              << ", \"total_reward\": " << total_reward
              << ", \"termination_reason\": \"" << step_res.termination_reason << "\"}\n";
    return 0;
}

int main(int argc, char** argv) {
    try {
        if (argc < 2) {
            throw std::runtime_error(
                "usage: veap-rl train MODEL SEED | eval MODEL | infer MODEL STATE |\n"
                "               replay-tape TAPE OUT [COMPARE] |\n"
                "               train-physics MODEL SEED [EPISODES] | eval-physics MODEL | infer-physics MODEL X Y"
            );
        }

        std::string command = argv[1];

        // 1. Control tape replay through C/C++ physics environment
        if (command == "replay-tape") {
            if (argc < 4) throw std::runtime_error("usage: veap-rl replay-tape TAPE_JSON OUT_JSON [COMPARE_JSON]");
            std::string tape_path = argv[2];
            std::string out_path = argv[3];
            std::string compare_path = (argc >= 5) ? argv[4] : "";
            veap::PhysicsEnv env;
            bool ok = env.replay_control_tape(tape_path, out_path, compare_path);
            return ok ? 0 : 1;
        }

        // 2. Physics environment RL training
        if (command == "train-physics") {
            if (argc < 4) throw std::runtime_error("usage: veap-rl train-physics MODEL SEED [EPISODES]");
            std::string model_path = argv[2];
            unsigned seed = static_cast<unsigned>(std::stoul(argv[3]));
            int episodes = (argc >= 5) ? std::stoi(argv[4]) : 2000;
            PhysPolicy policy{};
            train_physics(policy, seed, episodes);
            save_phys(policy, model_path);
            std::cout << "{\"training\": \"physics_env\", \"episodes\": " << episodes
                      << ", \"seed\": " << seed << ", \"out\": \"" << model_path << "\"}\n";
            return 0;
        }

        // 3. Physics environment evaluation
        if (command == "eval-physics") {
            if (argc < 3) throw std::runtime_error("usage: veap-rl eval-physics MODEL");
            auto policy = load_phys(argv[2]);
            return evaluate_physics(policy);
        }

        // 4. Physics environment inference
        if (command == "infer-physics") {
            if (argc < 5) throw std::runtime_error("usage: veap-rl infer-physics MODEL X Y");
            auto policy = load_phys(argv[2]);
            double x = std::stod(argv[3]);
            double y = std::stod(argv[4]);
            int s = quantize_state(x, y);
            int a = veap_greedy(policy[s].data());
            std::cout << "{\"state_idx\": " << s << ", \"action\": " << a << "}\n";
            return 0;
        }

        // Original grid commands
        if (command == "train" && argc == 4) {
            std::string input = argv[3];
            if (input.empty() || input.find_first_not_of("0123456789") != std::string::npos)
                throw std::runtime_error("invalid seed");
            auto seed = std::stoull(input);
            if (seed > UINT32_MAX) throw std::runtime_error("seed exceeds uint32");
            Policy policy{};
            train(policy, static_cast<unsigned>(seed));
            save(policy, argv[2]);
            return 0;
        }

        auto policy = load(argv[2]);
        if (command == "eval" && argc == 3) return evaluate(policy);
        if (command == "infer" && argc == 4) {
            std::string input = argv[3];
            if (input.empty() || input.find_first_not_of("0123456789") != std::string::npos)
                throw std::runtime_error("invalid state");
            int s = std::stoi(input);
            if (s >= goal || blocked(s)) throw std::runtime_error("state must be traversable and nonterminal");
            std::cout << veap_greedy(policy[s].data()) << '\n';
            return 0;
        }

        throw std::runtime_error("unsupported command or argument count");
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n';
        return 2;
    }
}
