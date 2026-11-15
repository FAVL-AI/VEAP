export function RawMessage({ sample }) {
  return <pre>{JSON.stringify(sample, null, 2)}</pre>;
}

export function SampleTable({ sample }) {
  if (!sample) return <p>No sample selected.</p>;
  return (
    <table>
      <tbody>
        {Object.entries(sample).map(([key, value]) => (
          <tr key={key}>
            <th scope="row">{key}</th>
            <td>{typeof value === "object" ? JSON.stringify(value) : String(value)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function RlMetricsPanel({ sample }) {
  if (!sample) return <p>No sample selected.</p>;

  const obs = sample.observation;
  const hasRl = Boolean(obs);

  if (!hasRl) {
    return (
      <div className="rl-panel-notice">
        <p>
          <em>Raw physics trace source.</em> Switch engine to <strong>Native RL (C/C++ Physics)</strong> to inspect active RL observations, reward signals, and termination reasons.
        </p>
      </div>
    );
  }

  return (
    <div className="rl-metrics">
      <div className="metric-cards">
        <div className="card">
          <span className="card-label">Step Reward</span>
          <span className="card-value reward-val">
            {typeof sample.reward === "number" ? sample.reward.toFixed(4) : "—"}
          </span>
        </div>
        <div className="card">
          <span className="card-label">Cumulative Reward</span>
          <span className="card-value">
            {typeof sample.cumulative_reward === "number" ? sample.cumulative_reward.toFixed(4) : "—"}
          </span>
        </div>
        <div className="card">
          <span className="card-label">Termination Status</span>
          <span className={`card-badge ${sample.terminated ? "badge-term" : sample.truncated ? "badge-trunc" : "badge-live"}`}>
            {sample.terminated ? "Terminated" : sample.truncated ? "Truncated" : "Active"}
          </span>
        </div>
        <div className="card">
          <span className="card-label">Termination Reason</span>
          <span className="card-value reason-val">
            {sample.termination_reason || "in_progress"}
          </span>
        </div>
      </div>

      <div className="obs-summary">
        <h3>Current Observation State</h3>
        <dl className="obs-grid">
          <div>
            <dt>Agent Position (X, Y)</dt>
            <dd>({obs.x.toFixed(3)}, {obs.y.toFixed(3)}) m</dd>
          </div>
          <div>
            <dt>Linear Velocity (Vx, Vy)</dt>
            <dd>({obs.vx.toFixed(3)}, {obs.vy.toFixed(3)}) m/s</dd>
          </div>
          <div>
            <dt>Target Coords</dt>
            <dd>({obs.target_x.toFixed(2)}, {obs.target_y.toFixed(2)}) m</dd>
          </div>
          <div>
            <dt>Distance to Target</dt>
            <dd className="target-dist">{obs.dist_to_target.toFixed(3)} m</dd>
          </div>
          <div>
            <dt>Active Waypoint Index</dt>
            <dd>{obs.waypoint_index}</dd>
          </div>
          <div>
            <dt>Constraint Safety</dt>
            <dd className={obs.in_violation ? "violation-flag" : "safe-flag"}>
              {obs.in_violation ? "Collision / Boundary Violation" : "Cleared (Safe)"}
            </dd>
          </div>
        </dl>
      </div>
    </div>
  );
}

export function PhysicsVerificationPanel({ sample }) {
  if (!sample) return <p>No sample selected.</p>;

  const cmd = sample.command_vx_vy_yaw || [0, 0, 0];
  const pos = sample.position_xyz_m || [0, 0, 0];
  const vel = sample.velocity_xyz_m_s || [0, 0, 0];
  const quat = sample.orientation_xyzw || [0, 0, 0, 1];
  const expectedTime = (sample.tick * 0.2).toFixed(4);
  const actualTime = sample.time_s.toFixed(4);
  const timeSynced = Math.abs(parseFloat(actualTime) - parseFloat(expectedTime)) < 1e-4;

  return (
    <div className="verification-panel">
      <div className="verif-row">
        <strong>Time Grid Integrity:</strong>{" "}
        <span className={timeSynced ? "safe-flag" : "violation-flag"}>
          {timeSynced ? `Synchronized (${actualTime}s = tick ${sample.tick} × 0.2s)` : `Grid Mismatch (${actualTime}s vs ${expectedTime}s)`}
        </span>
      </div>

      <div className="verif-section">
        <h3>Commanded Velocity Tape Action</h3>
        <p>Vx: {cmd[0].toFixed(3)} m/s · Vy: {cmd[1].toFixed(3)} m/s · Yaw rate: {cmd[2].toFixed(3)} rad/s</p>
      </div>

      <div className="verif-section">
        <h3>Simulated State</h3>
        <p>Position: [{pos[0].toFixed(4)}, {pos[1].toFixed(4)}, {pos[2].toFixed(4)}] m</p>
        <p>Velocity: [{vel[0].toFixed(4)}, {vel[1].toFixed(4)}, {vel[2].toFixed(4)}] m/s</p>
        <p>Orientation: [{quat[0].toFixed(4)}, {quat[1].toFixed(4)}, {quat[2].toFixed(4)}, {quat[3].toFixed(4)}]</p>
        <p>Contacts / Violations: {sample.contacts !== null && sample.contacts !== undefined ? sample.contacts : "N/A"}</p>
      </div>
    </div>
  );
}

export const panels = {
  "RL Metrics & Step Info": RlMetricsPanel,
  "Physics Verification": PhysicsVerificationPanel,
  Table: SampleTable,
  "Raw Messages": RawMessage,
};
