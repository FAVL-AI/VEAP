CFLAGS ?= -O2 -std=c17 -Wall -Wextra -Werror
CXXFLAGS ?= -O2 -std=c++20 -Wall -Wextra -Werror
.PHONY: all check clean
all: build/veap-rl
build/policy.o: policy.c policy.h
	mkdir -p build
	$(CC) $(CFLAGS) -c policy.c -o $@
build/physics_env.o: physics_env.cpp physics_env.h
	mkdir -p build
	$(CXX) $(CXXFLAGS) -c physics_env.cpp -o $@
build/veap-rl: main.cpp build/policy.o build/physics_env.o
	$(CXX) $(CXXFLAGS) $^ -o $@
check: all
	sh check.sh
clean:
	rm -rf build
