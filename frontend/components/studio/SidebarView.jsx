export default function SidebarView() {
  return (
    <aside className={"sidebar"}>
      <div className={"brand"}>
        <div className={"brand-mark"}>
          {"V"}
          <span>{"∕"}</span>
        </div>
        <div>
          <div className={"brand-name"}>
            {"VEAP"}
            <span>{"®"}</span>
          </div>
          <div className={"brand-caption"}>{"ASSURANCE STUDIO"}</div>
        </div>
      </div>
      <div className={"workspace-tag"}>
        <span className={"status-dot"} />
        {" RESEARCH PILOT "}
        <span className={"tag-chevron"}>{"v0.5"}</span>
      </div>
      <div className={"nav-label"}>{"WORKSPACE"}</div>
      <nav className={"navigation"} aria-label={"Primary"}>
        <button className={"nav-link active"} data-view={"overview"}>
          <span>{"◈"}</span>
          {" Command center"}
        </button>
        <button className={"nav-link"} data-view={"experiments"}>
          <span>{"⌁"}</span>
          {" Experiment lab"}
        </button>
        <button className={"nav-link"} data-view={"evidence"}>
          <span>{"▤"}</span>
          {" Evidence vault"}
        </button>
        <button className={"nav-link"} data-view={"reviews"}>
          <span>{"◇"}</span>
          {" Human review"}
        </button>
        <button className={"nav-link"} data-view={"audit"}>
          <span>{"≋"}</span>
          {" Audit ledger"}
        </button>
        <button className={"nav-link"} data-view={"engines"}>
          <span>{"▦"}</span>
          {" Engine status"}
        </button>
        <a href="/replay">Native replay</a>
      </nav>
      <div className={"sidebar-bottom"}>
        <div className={"safety-callout"}>
          <div className={"callout-title"}>{"◉ INTEGRITY BOUNDARY"}</div>
          <p>
            {
              "Research-only evaluator. No robot motion commands. Imported evidence is not authenticated."
            }
          </p>
        </div>
        <div className={"sidebar-foot"}>
          {"VERIFIABLE BY DESIGN "}
          <span>{"·"}</span>
          {" NOT SAFETY CERTIFIED"}
        </div>
      </div>
    </aside>
  );
}
