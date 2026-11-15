import SidebarView from "./SidebarView";
import TopbarView from "./TopbarView";
import PageOverviewView from "./PageOverviewView";
import PageScenariosView from "./PageScenariosView";
import PageEvidenceView from "./PageEvidenceView";
import PageAgentsView from "./PageAgentsView";
import PageResearchView from "./PageResearchView";
import CopyrightView from "./CopyrightView";
export default function Workspace() {
  return (
    <>
      <div className={"shell"}>
        <SidebarView />
        <div className={"workarea"}>
          <TopbarView />
          <PageOverviewView />
          <PageScenariosView />
          <PageEvidenceView />
          <PageAgentsView />
          <PageResearchView />
          <CopyrightView />
        </div>
      </div>
      <div
        className={"toast"}
        id={"toast"}
        role={"status"}
        aria-live={"polite"}
      />
      <div
        id={"auth-modal"}
        className={"modal-wrap hidden"}
        role={"dialog"}
        aria-modal={"true"}
        aria-labelledby={"auth-title"}
      >
        <div className={"modal"}>
          <div className={"eyebrow"}>{"PRIVATE CONTROL PLANE"}</div>
          <h2 id={"auth-title"}>{"API access token"}</h2>
          <p>
            {
              "For authenticated deployments, enter the VEAP_ADMIN_TOKEN set on the server. The token stays in this page's memory, not browser storage."
            }
          </p>
          <input
            type={"password"}
            id={"auth-input"}
            className={"field"}
            placeholder={"Bearer token"}
            autoComplete={"off"}
          />
          <div className={"modal-actions"}>
            <button className={"button-secondary"} id={"auth-cancel"}>
              {"Cancel"}
            </button>
            <button className={"button-primary"} id={"auth-save"}>
              {"Connect"}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
