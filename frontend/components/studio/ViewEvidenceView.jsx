export default function ViewEvidenceView() {
  return (
    <section className={"view"} id={"view-evidence"} hidden>
      <div className={"page-top"}>
        <div>
          <div className={"eyebrow"}>{"FORENSIC RECORDS"}</div>
          <h1>
            {"Evidence vault"}
            <span className={"accent"}>{"."}</span>
          </h1>
          <p>
            {
              "Read-only uploads with content checksums, provenance labels and tenant-scoped access."
            }
          </p>
        </div>
      </div>
      <div className={"panel padded"}>
        <div className={"panel-head"}>
          <h2>{"Import recorded telemetry"}</h2>
          <span className={"panel-chip"}>
            {"MAX 12 MiB · NO ROBOT CONTROL"}
          </span>
        </div>
        <p>
          {
            "Accepts a raw JSON object, positional JSONL, or an MCAP file. MCAP is stored as an opaque container, not decoded or attested."
          }
        </p>
        <div className={"file-upload"}>
          <input
            id={"evidence-file"}
            type={"file"}
            accept={".jsonl,.json,.mcap"}
          />
          <button
            id={"upload-evidence"}
            className={"primary-btn"}
            type={"button"}
          >
            {"Upload read-only evidence"}
          </button>
        </div>
        <div className={"table-wrap"}>
          <table>
            <thead>
              <tr>
                <th>{"FILENAME"}</th>
                <th>{"FORMAT"}</th>
                <th>{"SIZE"}</th>
                <th>{"SHA256"}</th>
                <th>{"STATUS"}</th>
              </tr>
            </thead>
            <tbody id={"evidence-table"} />
          </table>
        </div>
      </div>
    </section>
  );
}
