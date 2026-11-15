export default function ViewEnginesView() {
  return (
    <section className={"view"} id={"view-engines"} hidden>
      <div className={"page-top"}>
        <div>
          <div className={"eyebrow"}>
            {"SIMULATION AND PHYSICAL INTERFACES"}
          </div>
          <h1>
            {"Engine readiness"}
            <span className={"accent"}>{"."}</span>
          </h1>
          <p>
            {
              "Inspect installed runtime adapters and download public 3D interchange assets. Exported geometry is not a completed native physics evaluation."
            }
          </p>
        </div>
      </div>
      <div className={"engine-grid"} id={"engine-grid"} />
      <div className={"panel padded"}>
        <h2>{"Scenario interchange files"}</h2>
        <p>
          {
            "Canonical surrogate geometry is available for engineering inspection. CAD properties are not vendor-calibrated."
          }
        </p>
        <div id={"asset-links"} className={"asset-links"} />
      </div>
    </section>
  );
}
