export default function SelectedEventTracePanel() {
  return (
    <section className={"panel trace-panel"}>
      <div className={"panel-heading"}>
        <div>
          <div className={"overline"}>{"PROVENANCE / RAW EVENTS"}</div>
          <h2>{"Selected event trace"}</h2>
        </div>
        <button
          className={"outline-button slim"}
          type={"button"}
          id={"evidence-export"}
          disabled
        >
          {"⇩ Export JSON"}
        </button>
      </div>
      <pre className={"trace-preview"} id={"trace-preview"}>
        {"Choose a completed run to inspect event provenance."}
      </pre>
    </section>
  );
}
