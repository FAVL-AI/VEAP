export default function RunControlPanel() {
  return (
    <section className={"panel run-panel"}>
      <div className={"panel-heading"}>
        <div>
          <div className={"overline"}>{"CONFIGURATION / EXPERIMENT"}</div>
          <h2>{"Run control"}</h2>
        </div>
        <span className={"tiny-label"}>{"EXPERIMENT 01"}</span>
      </div>
      <div className={"panel-body"}>
        <label className={"field-label"} htmlFor={"scenario-select"}>
          {"SCENARIO CONTRACT"}
        </label>
        <select id={"scenario-select"} className={"field"}>
          <option>{"Loading scenarios..."}</option>
        </select>
        <div className={"field-hint"} id={"scenario-description"}>
          {"Reproducible benchmark environment"}
        </div>
        <div className={"field-two"}>
          <div>
            <label className={"field-label"} htmlFor={"policy-select"}>
              {"AGENT BASELINE"}
            </label>
            <select id={"policy-select"} className={"field"}>
              <option defaultValue={"route"}>{"Route planner"}</option>
              <option defaultValue={"greedy"}>{"Greedy baseline"}</option>
            </select>
          </div>
          <div>
            <label className={"field-label"} htmlFor={"seed-input"}>
              {"DETERMINISTIC SEED"}
            </label>
            <input
              id={"seed-input"}
              className={"field"}
              type={"number"}
              min={"0"}
              max={"4294967295"}
              defaultValue={"17"}
            />
          </div>
        </div>
        <div className={"toggle-row"}>
          <div>
            <strong>{"Geometric safety gate"}</strong>
            <p>{"Filter proposed velocities before execution"}</p>
          </div>
          <label className={"switch"}>
            <input id={"shield-toggle"} type={"checkbox"} defaultChecked />
            <span className={"switch-track"} />
          </label>
        </div>
        <button
          type={"button"}
          className={"button-primary full-button"}
          id={"run-control"}
        >
          {"▶   Execute benchmark run"}
        </button>
        <div className={"line-divider"} />
        <div className={"verification-heading"}>
          <span>{"INDEPENDENT VERIFICATION"}</span>
          <span className={"verif-state"} id={"verif-status"}>
            {"AWAITING EVIDENCE"}
          </span>
        </div>
        <div className={"gate"} data-gate={"chain"}>
          <span className={"gate-icon"}>{"◆"}</span>
          <span>{"Event-chain integrity"}</span>
          <b>{"—"}</b>
        </div>
        <div className={"gate"} data-gate={"postcondition"}>
          <span className={"gate-icon"}>{"⊙"}</span>
          <span>{"Task postconditions"}</span>
          <b>{"—"}</b>
        </div>
        <div className={"gate"} data-gate={"safety"}>
          <span className={"gate-icon"}>{"⬡"}</span>
          <span>{"Constraint satisfaction"}</span>
          <b>{"—"}</b>
        </div>
        <div className={"gate"} data-gate={"attestation"}>
          <span className={"gate-icon"}>{"⌘"}</span>
          <span>{"External attestation"}</span>
          <b>{"—"}</b>
        </div>
        <button
          type={"button"}
          className={"outline-button full-button"}
          id={"download-evidence"}
          disabled
        >
          {"⇩   Export evidence bundle"}
        </button>
      </div>
    </section>
  );
}
