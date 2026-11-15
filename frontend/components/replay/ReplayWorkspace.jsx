"use client";
import { useState } from "react";
import { panels } from "./TracePanels";
export default function ReplayWorkspace({ sources }) {
  const [source, setSource] = useState(Object.keys(sources)[0]);
  const [tick, setTick] = useState(0);
  const [layout, setLayout] = useState(["Table"]);
  const [choice, setChoice] = useState("Raw Messages");
  const samples = sources[source];
  return (
    <main className="replay">
      <nav>
        <a href="/">Observatory</a> · <a href="/studio">Assurance Studio</a>
      </nav>
      <h1>Native replay</h1>
      <label>
        Recorded engine{" "}
        <select
          value={source}
          onChange={(e) => {
            setSource(e.target.value);
            setTick(0);
          }}
        >
          {Object.keys(sources).map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
      </label>
      <label>
        Sample {tick + 1} of {samples.length}{" "}
        <input
          type="range"
          min="0"
          max={samples.length - 1}
          value={tick}
          onChange={(e) => setTick(Number(e.target.value))}
        />
      </label>
      <div>
        <select
          aria-label="Panel type"
          value={choice}
          onChange={(e) => setChoice(e.target.value)}
        >
          {Object.keys(panels).map((t) => (
            <option key={t}>{t}</option>
          ))}
        </select>
        <button onClick={() => setLayout([...layout, choice])}>
          Add panel
        </button>
      </div>
      <div className="panels">
        {layout.map((name, i) => {
          const Panel = panels[name];
          return (
            <section key={i}>
              <header>
                <h2>{name}</h2>
                <button
                  aria-label={"Remove " + name}
                  onClick={() => setLayout(layout.filter((_, j) => j !== i))}
                >
                  Remove
                </button>
              </header>
              <Panel sample={samples[tick]} />
            </section>
          );
        })}
      </div>
    </main>
  );
}
