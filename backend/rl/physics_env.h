#ifndef VEAP_RL_PHYSICS_ENV_H
#define VEAP_RL_PHYSICS_ENV_H

#include <array>
#include <string>
#include <vector>

namespace veap {

struct Obstacle {
    double x;
    double y;
    double radius;
    std::string label;
};

struct ForbiddenZone {
    double x1;
    double y1;
    double x2;
    double y2;
    std::string label;
};

struct Waypoint {
    double x;
    double y;
    std::string label;
};

struct Observation {
    double x;
    double y;
    double vx;
    double vy;
    double target_x;
    double target_y;
    double dist_to_target;
    int waypoint_index;
    bool in_violation;
};

struct StepResult {
    Observation observation;
    double reward;
    double cumulative_reward;
    bool terminated;
    bool truncated;
    std::string termination_reason;

    // Telemetry and verification fields
    int tick;
    double time_s;
    std::array<double, 3> command_vx_vy_yaw;
    std::array<double, 3> position_xyz_m;
    std::array<double, 3> velocity_xyz_m_s;
    std::array<double, 4> orientation_xyzw;
    double angular_z_rad_s;
    int contacts;
};

class PhysicsEnv {
public:
    PhysicsEnv();

    StepResult reset(double start_x = 1.2, double start_y = 1.3, double start_yaw = 0.0);
    StepResult step(const std::array<double, 3>& cmd_vx_vy_yaw);
    StepResult step_discrete(int action);

    bool check_collision(double px, double py) const;
    Observation get_observation() const;

    // Control tape replay and verification against existing native trace
    bool replay_control_tape(
        const std::string& tape_path,
        const std::string& output_trace_path,
        const std::string& compare_trace_path = ""
    );

    int current_tick() const { return tick_; }
    double current_time() const { return time_s_; }

private:
    double x_;
    double y_;
    double z_;
    double vx_;
    double vy_;
    double vz_;
    double yaw_;
    double omega_z_;
    int tick_;
    double time_s_;
    int stage_;
    double cumulative_reward_;

    // Scenario geometry and constraints
    std::vector<Obstacle> obstacles_;
    std::vector<ForbiddenZone> forbidden_zones_;
    std::vector<Waypoint> waypoints_;

    double dt_;
    int substeps_;
    double dt_sub_;
    double robot_radius_;
    double mass_;
    double damping_;
    double kp_;
    double u_max_;
    double waypoint_tolerance_;
};

} // namespace veap

#endif

