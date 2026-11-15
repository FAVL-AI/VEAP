export default function SimulatorModelAndDeviceAdaptersPanel() {
  return (
    <section className={"panel explanation"}>
      <div className={"overline"}>{"EXTENSION BOUNDARY"}</div>
      <h2>{"Simulator, model, and device adapters"}</h2>
      <p>
        {
          "Physical robot commands are deliberately excluded. The next adapter layer consumes ROS 2/MCAP or Isaac Lab evidence as read-only observations. Real robot actuation must remain behind a separately reviewed, hardware-enforced safety supervisor."
        }
      </p>
    </section>
  );
}
