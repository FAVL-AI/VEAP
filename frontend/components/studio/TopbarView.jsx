export default function TopbarView() {
  return (
    <header className={"topbar"}>
      <div className={"breadcrumbs"}>
        {"PLATFORM "}
        <span>{" / "}</span>
        <b id={"current-view"}>{"Command center"}</b>
      </div>
      <div className={"topbar-right"}>
        <span className={"api-status"} id={"service-status"}>
          {"● LOCAL INSTANCE"}
        </span>
        <div className={"user-pill"} id={"user-pill"}>
          {"Not connected"}
        </div>
        <button
          id={"disconnect"}
          className={"secondary-btn small"}
          type={"button"}
        >
          {"Disconnect"}
        </button>
      </div>
    </header>
  );
}
