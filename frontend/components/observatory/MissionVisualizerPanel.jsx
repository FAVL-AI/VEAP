export default function MissionVisualizerPanel() {
  return (
    <section className={"panel viewport-panel"}>
      <div className={"panel-heading"}>
        <div>
          <div className={"overline"}>{"ENVIRONMENT / WORLD VIEW"}</div>
          <h2>
            {"Mission visualizer "}
            <span id={"scenario-label"} className={"muted-label"}>
              {"Warehouse · multi-stop transfer"}
            </span>
          </h2>
        </div>
        <div className={"status-indicator"}>
          <span className={"green-dot"} />
          <span id={"scene-status"}>{"PREVIEW"}</span>
        </div>
      </div>
      <div className={"world-container"}>
        <canvas
          id={"world"}
          role={"img"}
          aria-label={
            "Interactive isometric simulation of map, hazards, objectives, robot, and verified trajectory"
          }
        />
        <div className={"world-label-top"}>
          <span className={"live-mini"}>{"● WORLD MODEL"}</span>
          <span className={"world-spec"}>{"2D DYNAMICS · 3D PROJECTION"}</span>
        </div>
        <div className={"world-compass"}>
          <b>{"N"}</b>
          <span className={"compass-cross"}>{"✣"}</span>
          <small>{"ROTATE"}</small>
        </div>
        <div className={"world-bottom"}>
          <span>
            <i className={"legend-dot robot"} />
            {" Agent"}
          </span>
          <span>
            <i className={"legend-dot objective"} />
            {" Objective"}
          </span>
          <span>
            <i className={"legend-dot hazard"} />
            {" Restricted zone"}
          </span>
          <span>
            <i className={"legend-dot trail"} />
            {" Trajectory"}
          </span>
        </div>
        <div className={"world-help"}>{"DRAG TO ORBIT · SCROLL TO ZOOM"}</div>
      </div>
      <div className={"playback-strip"}>
        <button
          id={"play-pause"}
          type={"button"}
          className={"play-button"}
          aria-label={"Play or pause trajectory"}
        >
          {"▶"}
        </button>
        <div className={"playback-time"} id={"playback-time"}>
          {"T+ 00.0s"}
        </div>
        <input
          id={"scrubber"}
          type={"range"}
          min={"0"}
          max={"100"}
          defaultValue={"0"}
          aria-label={"Trajectory playback progress"}
        />
        <div className={"playback-time"} id={"playback-total"}>
          {"—"}
        </div>
        <button
          id={"reset-camera"}
          type={"button"}
          className={"tiny-button"}
          title={"Reset camera orbit"}
        >
          {"⟲"}
        </button>
      </div>
    </section>
  );
}
