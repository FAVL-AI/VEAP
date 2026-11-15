export default function ViewExperimentsView() {
  return (
    <section className={"view"} id={"view-experiments"} hidden>
      <div className={"page-top"}>
        <div>
          <div className={"eyebrow"}>{"REPRODUCIBLE EXPERIMENTATION"}</div>
          <h1>
            {"Experiment lab"}
            <span className={"accent"}>{"."}</span>
          </h1>
          <p>
            {
              "Inspect seeded runs, captured traces and evidence status without trusting a model's completion claim."
            }
          </p>
        </div>
      </div>
      <div className={"panel padded"}>
        <h2>{"Execution records"}</h2>
        <div className={"table-wrap"}>
          <table>
            <thead>
              <tr>
                <th>{"ID"}</th>
                <th>{"SCENARIO"}</th>
                <th>{"POLICY"}</th>
                <th>{"SEED"}</th>
                <th>{"STATUS"}</th>
                <th>{"VIOLATIONS"}</th>
              </tr>
            </thead>
            <tbody id={"experiments-table"} />
          </table>
        </div>
        <h3>{"Selected verifier record"}</h3>
        <pre id={"selected-run-json"}>{"No run selected."}</pre>
      </div>
    </section>
  );
}
