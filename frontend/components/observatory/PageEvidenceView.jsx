import RecordedExperimentsPanel from "./RecordedExperimentsPanel";
import SelectedEventTracePanel from "./SelectedEventTracePanel";
export default function PageEvidenceView() {
  return (
    <main id={"page-evidence"} className={"page subpage"}>
      <div className={"section-head"}>
        <div className={"eyebrow"}>{"PROVENANCE / AUDIT"}</div>
        <h1>
          {"Evidence ledger"}
          <span className={"title-dot"}>{"."}</span>
        </h1>
        <p>
          {
            "Inspectable action-observation chains and downloadable deterministic run bundles."
          }
        </p>
      </div>
      <RecordedExperimentsPanel />
      <SelectedEventTracePanel />
    </main>
  );
}
