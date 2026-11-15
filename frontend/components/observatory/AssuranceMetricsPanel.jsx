export default function AssuranceMetricsPanel() {
  return (
    <section className={"panel analytics-panel"}>
      <div className={"panel-heading"}>
        <div>
          <div className={"overline"}>{"EVALUATION / LAST RUN"}</div>
          <h2>{"Assurance metrics"}</h2>
        </div>
        <span className={"tiny-label"} id={"analysis-run-tag"}>
          {"NO RUN"}
        </span>
      </div>
      <div className={"analysis-body"}>
        <div className={"assurance-score"}>
          <div>
            <span className={"subtle"}>{"VERIFIED PROGRESS"}</span>
            <strong id={"run-progress"}>{"—"}</strong>
          </div>
          <div className={"progress-track"}>
            <div id={"run-progress-bar"} className={"progress-fill"} />
          </div>
        </div>
        <div className={"metric-row"}>
          <span>{"Minimum obstacle clearance"}</span>
          <b id={"last-clearance"}>{"—"}</b>
        </div>
        <div className={"metric-row"}>
          <span>{"Faults / recovered"}</span>
          <b id={"last-faults"}>{"—"}</b>
        </div>
        <div className={"metric-row"}>
          <span>{"Simulated episode duration"}</span>
          <b id={"last-duration"}>{"—"}</b>
        </div>
        <div className={"metric-row"}>
          <span>
            {"Energy proxy "}
            <small>{"(not J)"}</small>
          </span>
          <b id={"last-energy"}>{"—"}</b>
        </div>
        <p className={"scope-note"}>
          {
            "These measurements come from a planar toy simulator. They do not establish real-world safety or physics validity."
          }
        </p>
      </div>
    </section>
  );
}
