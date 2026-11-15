#include "policy.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <cstdlib>
#include <unistd.h>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

using Row = std::array<double, 4>;
using Policy = std::array<Row, 36>;
// Versioned synthetic navigation environment. Coordinates are row-major.
constexpr std::array<const char*,6> map = {"......",".###..","...#..",".#....",".#.#..",".....G"};
constexpr int goal = 35;
bool blocked(int s) { return map[s/6][s%6] == '#'; }
int move_agent(int s, int a) {
    constexpr int dx[] = {0,1,0,-1}, dy[] = {-1,0,1,0};
    int x = s%6 + dx[a], y = s/6 + dy[a];
    if (x < 0 || y < 0 || x >= 6 || y >= 6 || blocked(y*6+x)) return s;
    return y*6+x;
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
    std::uniform_int_distribution<int> start(0,34), action(0,3);
    std::bernoulli_distribution explore(0.25);
    for (int episode=0; episode<5000; ++episode) {
        int s;
        do { s=start(rng); } while (blocked(s));
        for (int step=0; step<80 && s!=goal; ++step) {
            int a=explore(rng) ? action(rng) : veap_greedy(policy[s].data());
            int next=move_agent(s,a);
            double reward=next==goal ? 10.0 : (next==s ? -2.0 : -0.1);
            policy[s][a]=veap_q_update(policy[s][a],reward,policy[next].data(),next==goal,0.2,0.95);
            s=next;
        }
    }
}
int evaluate(const Policy& policy) {
    int successes=0, starts=0, transitions=0;
    for (int s=0;s<goal;++s) {
        if (blocked(s)) continue;
        ++starts;
        int pos=s;
        for (int t=0;t<80 && pos!=goal;++t) {
            pos=move_agent(pos,veap_greedy(policy[pos].data()));
            ++transitions;
        }
        successes += pos==goal;
    }
    std::cout << "{\"starts\":" << starts << ",\"successes\":" << successes
              << ",\"transitions\":" << transitions << "}\n";
    return successes==starts ? 0 : 1;
}
int main(int argc,char** argv) {
    try {
        if (argc<3) throw std::runtime_error("usage: veap-rl train MODEL SEED | eval MODEL | infer MODEL STATE");
        std::string command=argv[1];
        if (command=="train" && argc==4) {
            std::string input=argv[3];
            if (input.empty() || input.find_first_not_of("0123456789")!=std::string::npos)
                throw std::runtime_error("invalid seed");
            auto seed=std::stoull(input);
            if (seed>UINT32_MAX) throw std::runtime_error("seed exceeds uint32");
            Policy policy{};
            train(policy,static_cast<unsigned>(seed));
            save(policy,argv[2]);
            return 0;
        }
        auto policy=load(argv[2]);
        if (command=="eval" && argc==3) return evaluate(policy);
        if (command=="infer" && argc==4) {
            std::string input=argv[3];
            if (input.empty() || input.find_first_not_of("0123456789")!=std::string::npos)
                throw std::runtime_error("invalid state");
            int s=std::stoi(input);
            if (s>=goal || blocked(s)) throw std::runtime_error("state must be traversable and nonterminal");
            std::cout << veap_greedy(policy[s].data()) << '\n';
            return 0;
        }
        throw std::runtime_error("unsupported command or argument count");
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 2; }
}
