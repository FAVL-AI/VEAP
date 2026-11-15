export default function PageScenariosView() {
  return (
    <main id={"page-scenarios"} className={"page subpage"}>
      <div className={"section-head"}>
        <div className={"eyebrow"}>{"DATASETS / EVALUATION TASKS"}</div>
        <h1>
          {"Scenario library"}
          <span className={"title-dot"}>{"."}</span>
        </h1>
        <p>
          {
            "Immutable, split-labelled task definitions. Evaluation uses independently checked postconditions."
          }
        </p>
      </div>
      <div id={"scenario-cards"} className={"scenario-cards"} />
    </main>
  );
}
