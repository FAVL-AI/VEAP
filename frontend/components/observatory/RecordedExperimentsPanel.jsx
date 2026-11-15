export default function RecordedExperimentsPanel() {
  return (
    <section className={"panel"}>
      <div className={"panel-heading"}>
        <div>
          <div className={"overline"}>{"AUDIT / RECORDS"}</div>
          <h2>{"Recorded experiments"}</h2>
        </div>
        <span id={"run-count"} className={"tiny-label"}>
          {"0 RUNS"}
        </span>
      </div>
      <div className={"table-wrap"}>
        <table>
          <thead>
            <tr>
              <th>{"RUN ID"}</th>
              <th>{"SCENARIO"}</th>
              <th>{"POLICY"}</th>
              <th>{"SHIELD"}</th>
              <th>{"VERIFIED"}</th>
              <th>{"VIOLATIONS"}</th>
              <th>{"RECORDED"}</th>
            </tr>
          </thead>
          <tbody id={"run-table"}>
            <tr>
              <td colSpan={"7"}>{"No runs recorded."}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
}
