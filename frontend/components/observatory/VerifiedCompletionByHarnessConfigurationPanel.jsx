export default function VerifiedCompletionByHarnessConfigurationPanel() {
  return (
    <section className={"panel research-panel"}>
      <div className={"panel-heading"}>
        <div>
          <div className={"overline"}>{"COMPARISON / OBSERVED RECORDS"}</div>
          <h2>{"Verified completion by harness configuration"}</h2>
        </div>
        <button
          className={"button-secondary slim"}
          id={"research-compare"}
          type={"button"}
        >
          {"Run paired comparison"}
        </button>
      </div>
      <div id={"comparison-bars"} className={"comparison-bars"}>
        <p>
          {
            "No experiments yet. Run both policies against the same scenario and seed."
          }
        </p>
      </div>
    </section>
  );
}
