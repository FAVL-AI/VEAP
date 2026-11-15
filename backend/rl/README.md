# First native RL baseline
Run `make native-rl-check` from the repository root. Within backend/rl:
```sh
make
build/veap-rl train /tmp/veap-q17.model 17
build/veap-rl eval /tmp/veap-q17.model
build/veap-rl infer /tmp/veap-q17.model 0
```
Training runs 5,000 epsilon-greedy episodes against a fixed 6×6 synthetic grid with walls and a goal. Observations are cell IDs, actions are north/east/south/west, and blocked moves retain position. Rewards are +10 at the goal, −2 for blocked moves and −0.1 otherwise. The 80-step limit truncates an episode. The C update masks bootstrapping on goal termination and bootstraps across truncation. C++ handles sampling, checkpoint loading, evaluation and the CLI. Evaluation enumerates every traversable nonterminal start. This measures policy acquisition on one known map. Hardware, unseen scenes, continuous control, perception, deep networks and online robot training require separate experiments.
