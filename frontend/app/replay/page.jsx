import mujoco from "../../../artifacts/research/v06-mujoco-locked-replay.json";
import isaac from "../../../artifacts/research/v06-isaaclab-locked-replay.json";
import ReplayWorkspace from "../../components/replay/ReplayWorkspace";
import "./replay.css";
export default function ReplayPage() {
  return (
    <ReplayWorkspace
      sources={{
        MuJoCo: mujoco.trace.samples,
        "Isaac Lab": isaac.trace.samples,
      }}
    />
  );
}
