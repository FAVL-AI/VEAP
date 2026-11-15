export default function ViewAuditView() {
  return (
    <section className={"view"} id={"view-audit"} hidden>
      <div className={"page-top"}>
        <div>
          <div className={"eyebrow"}>{"PROVENANCE AND CHANGE HISTORY"}</div>
          <h1>
            {"Audit ledger"}
            <span className={"accent"}>{"."}</span>
          </h1>
          <p>
            {
              "Per-tenant SHA-256 event chaining. Local consistency does not prove independent provenance or immutability."
            }
          </p>
        </div>
      </div>
      <div className={"panel padded"}>
        <div className={"audit-tools"}>
          <button id={"verify-audit"} className={"primary-btn"} type={"button"}>
            {"Verify local audit chain"}
          </button>
          <span id={"audit-status"}>{"Not checked"}</span>
        </div>
        <div className={"table-wrap"}>
          <table>
            <thead>
              <tr>
                <th>{"EVENT"}</th>
                <th>{"ACTION"}</th>
                <th>{"ACTOR"}</th>
                <th>{"OBJECT"}</th>
                <th>{"SHA256"}</th>
              </tr>
            </thead>
            <tbody id={"audit-table"} />
          </table>
        </div>
      </div>
    </section>
  );
}
