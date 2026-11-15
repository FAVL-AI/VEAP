import VerifiedCompletionByHarnessConfigurationPanel from "./VerifiedCompletionByHarnessConfigurationPanel";
import PublicationGatesPanel from "./PublicationGatesPanel";
export default function PageResearchView() {
  return (
    <main id={"page-research"} className={"page subpage"}>
      <div className={"section-head"}>
        <div className={"eyebrow"}>{"METHODOLOGY / EXPERIMENTAL CONTROL"}</div>
        <h1>
          {"Research & ablations"}
          <span className={"title-dot"}>{"."}</span>
        </h1>
        <p>
          {
            "Compare matched baselines with safety gate on/off, fixed scenarios and reproducible seeds."
          }
        </p>
      </div>
      <VerifiedCompletionByHarnessConfigurationPanel />
      <PublicationGatesPanel />
    </main>
  );
}
