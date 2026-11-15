import mujoco from "../../../artifacts/research/v06-mujoco-locked-replay.json";
import isaac from "../../../artifacts/research/v06-isaaclab-locked-replay.json";
import rlNative from "../../../artifacts/research/v06-rl-physics-replay.json";
import ReplayWorkspace from "../../components/replay/ReplayWorkspace";
import "./replay.css";

export const metadata = {
  title: "VEAP · Native Physics & RL Trace Replay Workbench",
  description: "Inspect end-to-end native physics and reinforcement learning traces.",
};

export default function ReplayPage() {
  return (
    <ReplayWorkspace
      sources={{
        "Native RL (C/C++ Physics)": rlNative.trace.samples,
        MuJoCo: mujoco.trace.samples,
        "Isaac Lab": isaac.trace.samples,
      }}
    />
  );
}
