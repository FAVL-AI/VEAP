export default function EvidenceStreamPanel() {
  return (
    <section className={"panel events-panel"}>
      <div className={"panel-heading"}>
        <div>
          <div className={"overline"}>{"EXECUTION / INSTRUMENTATION"}</div>
          <h2>{"Evidence stream"}</h2>
        </div>
        <span id={"event-count"} className={"tiny-label"}>
          {"0 EVENTS"}
        </span>
      </div>
      <div className={"events-list"} id={"events-list"}>
        <div className={"empty-message"}>
          {
            "Select a scenario and execute a benchmark to generate trace events."
          }
        </div>
      </div>
    </section>
  );
}
