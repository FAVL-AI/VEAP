export default function TopbarView() {
  return (
    <header className={"topbar"}>
      <div className={"breadcrumbs"}>
        {"RESEARCH LAB "}
        <span>{"/"}</span>
        <b id={"breadcrumb"}>{"MISSION CONTROL"}</b>
      </div>
      <div className={"top-actions"}>
        <span className={"top-clock"} id={"live-clock"}>
          {"SESSION / LOCAL"}
        </span>
        <div className={"head-chip"}>
          <span className={"pulse-dot"} />
          {" Simulator online"}
        </div>
        <button
          type={"button"}
          id={"auth-button"}
          className={"avatar"}
          title={"Set API access token"}
        >
          {"VA"}
        </button>
      </div>
    </header>
  );
}
