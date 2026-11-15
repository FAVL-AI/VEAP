import MissionVisualizerPanel from "./MissionVisualizerPanel";
import RunControlPanel from "./RunControlPanel";
import EvidenceStreamPanel from "./EvidenceStreamPanel";
import AssuranceMetricsPanel from "./AssuranceMetricsPanel";
export default function PageOverviewView() {
  return (
    <main id={"page-overview"} className={"page active"}>
      <div className={"page-heading"}>
        <div>
          <div className={"eyebrow"}>
            <span className={"eyebrow-line"} />
            {" RESEARCH / AUTONOMY ASSURANCE"}
          </div>
          <h1>
            {"Verified autonomy"}
            <span className={"title-dot"}>{"."}</span>
            <br />
            <span className={"muted-title"}>{"Made observable."}</span>
          </h1>
          <p className={"intro"}>
            {
              "A reproducible proving ground for agent decisions, safety boundaries, fault recovery, and the evidence behind every outcome."
            }
          </p>
        </div>
        <div className={"heading-actions"}>
          <button
            type={"button"}
            className={"button-secondary"}
            id={"compare-trigger"}
          >
            <span>{"⇄"}</span>
            {" Compare policies"}
          </button>
          <button type={"button"} className={"button-primary"} id={"run-top"}>
            {"▶   Run experiment"}
          </button>
        </div>
      </div>
      <div className={"stats"} aria-label={"Observed metrics"}>
        <div className={"stat-card"}>
          <div className={"stat-label"}>
            {"VERIFIED COMPLETION "}
            <span className={"stat-glyph"}>{"◈"}</span>
          </div>
          <div className={"stat-number"} id={"metric-rate"}>
            {"—"}
          </div>
          <div className={"stat-detail"} id={"metric-rate-note"}>
            {"No evaluated trials yet"}
          </div>
        </div>
        <div className={"stat-card"}>
          <div className={"stat-label"}>
            {"UNSAFE EXECUTION EVENTS "}
            <span className={"stat-glyph orange"}>{"△"}</span>
          </div>
          <div className={"stat-number"} id={"metric-violations"}>
            {"—"}
          </div>
          <div className={"stat-detail"} id={"metric-violations-note"}>
            {"Computed by independent verifier"}
          </div>
        </div>
        <div className={"stat-card"}>
          <div className={"stat-label"}>
            {"SAFETY INTERVENTIONS "}
            <span className={"stat-glyph teal"}>{"✳"}</span>
          </div>
          <div className={"stat-number"} id={"metric-shields"}>
            {"—"}
          </div>
          <div className={"stat-detail"} id={"metric-shields-note"}>
            {"Actions modified by safety gate"}
          </div>
        </div>
        <div className={"stat-card"}>
          <div className={"stat-label"}>
            {"EVIDENCE EVENTS "}
            <span className={"stat-glyph violet"}>{"⌁"}</span>
          </div>
          <div className={"stat-number"} id={"metric-events"}>
            {"—"}
          </div>
          <div className={"stat-detail"} id={"metric-events-note"}>
            {"Hash-linked trajectory records"}
          </div>
        </div>
      </div>
      <div className={"main-grid"}>
        <MissionVisualizerPanel />
        <RunControlPanel />
      </div>
      <div className={"lower-grid"}>
        <EvidenceStreamPanel />
        <AssuranceMetricsPanel />
      </div>
    </main>
  );
}
