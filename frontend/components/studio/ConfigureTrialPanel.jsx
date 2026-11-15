export default function ConfigureTrialPanel() {
  return (
    <section className={"panel execute-panel"}>
      <div className={"panel-head"}>
        <div>
          <div className={"eyebrow"}>{"EXPERIMENT EXECUTION"}</div>
          <h2>{"Configure trial"}</h2>
        </div>
        <span className={"panel-chip"}>{"LOCAL TOY WORLD"}</span>
      </div>
      <div className={"panel-body"}>
        <label>{"SCENARIO CONTRACT"}</label>
        <select id={"scenario-select"} />
        <label>{"PLANNING BASELINE"}</label>
        <select id={"policy-select"}>
          <option defaultValue={"route"}>
            {"Route planner (mapped obstacles)"}
          </option>
          <option defaultValue={"greedy"}>
            {"Greedy navigation baseline"}
          </option>
        </select>
        <div className={"control-row"}>
          <div>
            <label htmlFor={"seed-input"}>{"SEED"}</label>
            <input
              id={"seed-input"}
              type={"number"}
              min={"0"}
              max={"4294967295"}
              defaultValue={"17"}
            />
          </div>
          <label className={"toggle-holder"}>
            <input id={"shield"} type={"checkbox"} defaultChecked />
            <span>{"Geometric safety gate"}</span>
          </label>
        </div>
        <button id={"execute"} className={"primary-btn launch"} type={"button"}>
          {"▶ Execute audited trial"}
        </button>
        <div className={"run-flag"}>
          <div className={"flag-label"}>{"LATEST VERIFICATION"}</div>
          <strong id={"verification-status"}>{"AWAITING EVIDENCE"}</strong>
          <small id={"verification-desc"}>
            {"No trial selected. Execution remains in the toy simulator."}
          </small>
        </div>
        <button
          id={"download-run"}
          className={"secondary-btn full"}
          type={"button"}
          disabled
        >
          {"↓ Export selected trace"}
        </button>
      </div>
    </section>
  );
}
