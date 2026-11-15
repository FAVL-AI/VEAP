import SidebarView from "./SidebarView";
import TopbarView from "./TopbarView";
import ViewOverviewView from "./ViewOverviewView";
import ViewExperimentsView from "./ViewExperimentsView";
import ViewEvidenceView from "./ViewEvidenceView";
import ViewReviewsView from "./ViewReviewsView";
import ViewAuditView from "./ViewAuditView";
import ViewEnginesView from "./ViewEnginesView";
import SiteFootView from "./SiteFootView";
export default function Workspace() {
  return (
    <>
      <div className={"app-shell"}>
        <SidebarView />
        <div className={"main-region"}>
          <TopbarView />
          <div className={"dashboard-main"}>
            <ViewOverviewView />
            <ViewExperimentsView />
            <ViewEvidenceView />
            <ViewReviewsView />
            <ViewAuditView />
            <ViewEnginesView />
            <SiteFootView />
          </div>
        </div>
      </div>
      <div className={"overlay"} id={"connect-overlay"}>
        <div className={"connect-card"}>
          <div className={"brand-mark large"}>
            {"V"}
            <span>{"∕"}</span>
          </div>
          <div className={"eyebrow"}>
            {"ENTERPRISE ACCESS / DEVELOPMENT PREVIEW"}
          </div>
          <h2>{"Connect to Assurance Studio"}</h2>
          <p>
            {
              "Enter a personal development token created with the local bootstrap CLI. This token is kept in page memory only; production SSO is not enabled in this pilot."
            }
          </p>
          <label htmlFor={"token-input"}>{"DEVELOPER BEARER TOKEN"}</label>
          <input
            type={"password"}
            id={"token-input"}
            placeholder={"veap_…"}
            autoComplete={"off"}
          />
          <button type={"button"} id={"connect"} className={"primary-btn full"}>
            {"Connect securely to local API"}
          </button>
          <p className={"connect-help"}>
            {"First-time setup: "}
            <code>
              {
                'python -m veap.enterprise.cli bootstrap --org "Pilot" --email you@example.org'
              }
            </code>
          </p>
          <div id={"connect-error"} className={"error-line"} role={"alert"} />
        </div>
      </div>
      <div
        className={"toast"}
        id={"toast"}
        role={"status"}
        aria-live={"polite"}
      />
    </>
  );
}
