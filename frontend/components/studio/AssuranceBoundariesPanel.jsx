export default function AssuranceBoundariesPanel() {
  return (
    <section className={"panel summary-panel"}>
      <div className={"panel-head"}>
        <div>
          <div className={"eyebrow"}>{"EVIDENCE / DECISION SUPPORT"}</div>
          <h2>{"Assurance boundaries"}</h2>
        </div>
      </div>
      <div className={"assurance-list"}>
        <div>
          <span>{"Execution verifier"}</span>
          <b>{"Agent-independent"}</b>
        </div>
        <div>
          <span>{"Sensor provenance"}</span>
          <b className={"pending"}>{"Unattested"}</b>
        </div>
        <div>
          <span>{"Physical fidelity"}</span>
          <b className={"pending"}>{"Not established"}</b>
        </div>
        <div>
          <span>{"Enterprise production"}</span>
          <b className={"pending"}>{"Not qualified"}</b>
        </div>
      </div>
      <p>
        {
          "Completed trials demonstrate execution against simplified scenario contracts. They cannot establish certified safety or sim-to-real generalisation."
        }
      </p>
    </section>
  );
}
