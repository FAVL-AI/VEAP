export default function SidebarView() {
  return (
    <aside className={"sidebar"}>
      <div className={"brandline"}>
        <div className={"brandmark"}>
          <span />
          <span />
          <span />
          <span />
        </div>
        <div>
          <strong>
            {"VEAP"}
            <span className={"accent"}>{"."}</span>
          </strong>
          <small>{"AGENT OBSERVATORY"}</small>
        </div>
      </div>
      <div className={"side-section-label"}>{"WORKSPACE"}</div>
      <nav className={"nav"} aria-label={"Main navigation"}>
        <button
          type={"button"}
          className={"navitem active"}
          data-page={"overview"}
        >
          <span className={"navicon"}>{"◈"}</span>
          {"Mission control"}
          <span className={"navshort"}>{"01"}</span>
        </button>
        <button type={"button"} className={"navitem"} data-page={"scenarios"}>
          <span className={"navicon"}>{"▦"}</span>
          {"Scenario library"}
          <span className={"navshort"}>{"02"}</span>
        </button>
        <button type={"button"} className={"navitem"} data-page={"evidence"}>
          <span className={"navicon"}>{"⌁"}</span>
          {"Evidence ledger"}
          <span className={"navshort"}>{"03"}</span>
        </button>
        <button type={"button"} className={"navitem"} data-page={"agents"}>
          <span className={"navicon"}>{"◇"}</span>
          {"Agent harness"}
          <span className={"navshort"}>{"04"}</span>
        </button>
        <button type={"button"} className={"navitem"} data-page={"research"}>
          <span className={"navicon"}>{"▤"}</span>
          {"Research & ablations"}
          <span className={"navshort"}>{"05"}</span>
        </button>
        <a href="/replay">Native replay</a>
      </nav>
      <div className={"side-section-label"}>{"RESEARCH PRINCIPLE"}</div>
      <div className={"side-quote"}>
        <span className={"quote-icon"}>{"“"}</span>
        {
          " An outcome is not evidence unless the trajectory can be independently checked. "
        }
        <div className={"quote-credit"}>{"VEAP DESIGN CONTRACT / V0.1"}</div>
      </div>
      <div className={"sidebar-footer"}>
        <div className={"footer-status"}>
          <span className={"status-dot"} />
          <span>{"LOCAL SIMULATION"}</span>
          <span className={"footer-version"}>{"v0.1.0"}</span>
        </div>
        <p>
          {"Read-only evaluation surface."}
          <br />
          {"No physical robot actuation."}
        </p>
      </div>
    </aside>
  );
}
