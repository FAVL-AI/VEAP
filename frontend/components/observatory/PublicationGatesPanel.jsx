export default function PublicationGatesPanel() {
  return (
    <section className={"panel explanation"}>
      <div className={"overline"}>{"RESEARCH VALIDITY"}</div>
      <h2>{"Publication gates—not satisfied by this demo"}</h2>
      <div className={"research-gates"}>
        <div>
          <b>{"01."}</b>
          {" Benchmark validity audit"}
        </div>
        <div>
          <b>{"02."}</b>
          {" Held-out contamination control"}
        </div>
        <div>
          <b>{"03."}</b>
          {" Multi-seed confidence intervals"}
        </div>
        <div>
          <b>{"04."}</b>
          {" External physics / hardware tests"}
        </div>
        <div>
          <b>{"05."}</b>
          {" Independent safety assurance"}
        </div>
        <div>
          <b>{"06."}</b>
          {" Latency, energy, and cost instrumentation"}
        </div>
      </div>
      <p>
        {"Run "}
        <code>{"python -m veap suite --seeds 0 1 2"}</code>
        {
          " to export the demo ablation matrix. Do not interpret toy-world scores as SOTA."
        }
      </p>
    </section>
  );
}
