export default function ViewReviewsView() {
  return (
    <section className={"view"} id={"view-reviews"} hidden>
      <div className={"page-top"}>
        <div>
          <div className={"eyebrow"}>{"INDEPENDENT HUMAN JUDGEMENT"}</div>
          <h1>
            {"Review board"}
            <span className={"accent"}>{"."}</span>
          </h1>
          <p>
            {
              "Reviewers cannot sign off their own experiment. Reviews remain distinguishable from independent ground truth."
            }
          </p>
        </div>
      </div>
      <div className={"panel padded"}>
        <h2>{"Review completed run"}</h2>
        <label htmlFor={"review-run"}>{"CHOOSE A RUN"}</label>
        <select id={"review-run"} />
        <label htmlFor={"review-decision"}>{"ASSESSMENT"}</label>
        <select id={"review-decision"}>
          <option defaultValue={"inconclusive"}>{"Inconclusive"}</option>
          <option defaultValue={"accepted"}>
            {"Accepted for research review"}
          </option>
          <option defaultValue={"rejected"}>
            {"Rejected for research review"}
          </option>
        </select>
        <label htmlFor={"review-notes"}>{"RATIONALE"}</label>
        <textarea
          id={"review-notes"}
          rows={"4"}
          placeholder={
            "Ground your decision in specific trace and scenario evidence, minimum 8 characters."
          }
        />
        <button id={"submit-review"} className={"primary-btn"} type={"button"}>
          {"Submit review"}
        </button>
        <h3>{"Recorded assessments"}</h3>
        <div id={"reviews-list"} className={"reviews-list"}>
          {"No run selected."}
        </div>
      </div>
    </section>
  );
}
