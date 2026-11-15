export default function RecentRunsPanel() {
  return (
    <section className={"panel"}>
      <div className={"panel-head"}>
        <div>
          <div className={"eyebrow"}>{"PROJECT / EXPERIMENTS"}</div>
          <h2>{"Recent runs"}</h2>
        </div>
        <span className={"panel-chip"} id={"run-count"}>
          {"0 RECORDS"}
        </span>
      </div>
      <div className={"table-wrap"}>
        <table>
          <thead>
            <tr>
              <th>{"RUN"}</th>
              <th>{"SCENARIO"}</th>
              <th>{"POLICY"}</th>
              <th>{"STATE"}</th>
              <th>{"VERIFIED"}</th>
            </tr>
          </thead>
          <tbody id={"run-table"}>
            <tr>
              <td colSpan={"5"} className={"muted-cell"}>
                {"Select a project to view experiments."}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
}
