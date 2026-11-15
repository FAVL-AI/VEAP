import LiveSimulationViewPanel from "./LiveSimulationViewPanel";
import ConfigureTrialPanel from "./ConfigureTrialPanel";
import RecentRunsPanel from "./RecentRunsPanel";
import AssuranceBoundariesPanel from "./AssuranceBoundariesPanel";
export default function ViewOverviewView() {
  return (
    <section className={"view"} id={"view-overview"}>
      <div className={"page-top"}>
        <div>
          <div className={"eyebrow"}>
            {"OPERATIONAL INTELLIGENCE / RESEARCH ENVIRONMENT"}
          </div>
          <h1>
            {"Evidence over assumptions"}
            <span className={"accent"}>{"."}</span>
          </h1>
          <p>
            {
              "Evaluate what autonomous agents actually demonstrate, under recorded conditions and independently checked constraints."
            }
          </p>
        </div>
        <div className={"corner-status"}>
          <span className={"fine"}>{"RELEASE CLASS"}</span>
          <strong>{"RESEARCH PILOT"}</strong>
          <small>{"Production qualification: not passed"}</small>
        </div>
      </div>
      <div className={"filters"}>
        <div className={"filter-box"}>
          <label htmlFor={"tenant-select"}>{"ORGANISATION"}</label>
          <select id={"tenant-select"} />
        </div>
        <div className={"filter-box"}>
          <label htmlFor={"project-select"}>{"PROJECT"}</label>
          <select id={"project-select"} />
        </div>
        <button id={"refresh"} className={"secondary-btn"} type={"button"}>
          {"↻ Refresh data"}
        </button>
        <button id={"new-project"} className={"primary-btn"} type={"button"}>
          {"+ New project"}
        </button>
      </div>
      <div className={"metrics-grid"}>
        <div className={"metric"}>
          <span>{"RECORDED RUNS"}</span>
          <strong id={"kpi-runs"}>{"—"}</strong>
          <small>{"Project scope"}</small>
        </div>
        <div className={"metric"}>
          <span>{"VERIFIER ACCEPTED"}</span>
          <strong id={"kpi-verified"}>{"—"}</strong>
          <small>{"Simulation postconditions"}</small>
        </div>
        <div className={"metric"}>
          <span>{"SAFETY VIOLATIONS"}</span>
          <strong id={"kpi-violations"}>{"—"}</strong>
          <small>{"Recorded geometry"}</small>
        </div>
        <div className={"metric"}>
          <span>{"UPLOADED EVIDENCE"}</span>
          <strong id={"kpi-evidence"}>{"—"}</strong>
          <small>{"Unattested external objects"}</small>
        </div>
      </div>
      <div className={"primary-grid"}>
        <LiveSimulationViewPanel />
        <ConfigureTrialPanel />
      </div>
      <div className={"lower-grid"}>
        <RecentRunsPanel />
        <AssuranceBoundariesPanel />
      </div>
    </section>
  );
}
