import SimulatorModelAndDeviceAdaptersPanel from "./SimulatorModelAndDeviceAdaptersPanel";
export default function PageAgentsView() {
  return (
    <main id={"page-agents"} className={"page subpage"}>
      <div className={"section-head"}>
        <div className={"eyebrow"}>{"HARNESS / EXECUTION ROLES"}</div>
        <h1>
          {"Agent architecture"}
          <span className={"title-dot"}>{"."}</span>
        </h1>
        <p>
          {
            "Separating decisions, execution control, and verification reduces self-grading and enables controlled ablations."
          }
        </p>
      </div>
      <div className={"agent-pipeline"}>
        <div className={"agent-node"}>
          <div className={"node-nr"}>{"01 / DECISION"}</div>
          <div className={"node-symbol"}>{"◇"}</div>
          <h3>{"Planning agent"}</h3>
          <p>
            {
              "Greedy and A* reference policies; bounded velocity proposals and inspectable decisions."
            }
          </p>
          <span>{"REFERENCE BASELINES · LIVE"}</span>
        </div>
        <div className={"pipeline-link"}>{"→"}</div>
        <div className={"agent-node"}>
          <div className={"node-nr"}>{"02 / CONTROL"}</div>
          <div className={"node-symbol"}>{"⌁"}</div>
          <h3>{"Execution harness"}</h3>
          <p>
            {
              "Deterministic clock, noisy observations, injected faults, and state transitions."
            }
          </p>
          <span>{"TOY SIMULATOR · LIVE"}</span>
        </div>
        <div className={"pipeline-link"}>{"→"}</div>
        <div className={"agent-node"}>
          <div className={"node-nr"}>{"03 / SAFETY"}</div>
          <div className={"node-symbol"}>{"⬡"}</div>
          <h3>{"Safety monitor"}</h3>
          <p>
            {
              "Independent geometric gate can clamp, redirect, or stop unsafe proposed motions."
            }
          </p>
          <span>{"NOT A FORMAL CBF · LIVE"}</span>
        </div>
        <div className={"pipeline-link"}>{"→"}</div>
        <div className={"agent-node"}>
          <div className={"node-nr"}>{"04 / AUDIT"}</div>
          <div className={"node-symbol"}>{"◈"}</div>
          <h3>{"Evidence verifier"}</h3>
          <p>
            {
              "Separately recomputes hazard contact, milestones, velocity consistency, and integrity."
            }
          </p>
          <span>{"READ-ONLY AUDITOR · LIVE"}</span>
        </div>
      </div>
      <SimulatorModelAndDeviceAdaptersPanel />
    </main>
  );
}
