export default function LiveSimulationViewPanel() {
  return (
    <section className={"panel world-panel"}>
      <div className={"panel-head"}>
        <div>
          <div className={"eyebrow"}>{"SCENARIO TWIN / GEOMETRY"}</div>
          <h2>{"Live simulation view"}</h2>
        </div>
        <span className={"panel-chip"}>{"ISOMETRIC · SURROGATE"}</span>
      </div>
      <div className={"viewport"}>
        <canvas
          id={"world"}
          aria-label={"Isometric scene and trajectory rendering"}
        />
        <div className={"viewport-head"}>
          {"VEAP SCENE TELEMETRY "}
          <span id={"scene-name"}>{"NO SCENE"}</span>
        </div>
        <div className={"viewport-foot"}>
          {"■ Obstacle   ■ Exclusion   ● Robot   ━ Trajectory"}
        </div>
      </div>
      <div className={"playback"}>
        <button id={"play"} className={"secondary-btn small"}>
          {"▶ Play trace"}
        </button>
        <input
          id={"scrub"}
          type={"range"}
          min={"0"}
          max={"100"}
          defaultValue={"0"}
          aria-label={"Trajectory position"}
        />
        <span id={"trace-tick"}>{"T+0"}</span>
      </div>
    </section>
  );
}
