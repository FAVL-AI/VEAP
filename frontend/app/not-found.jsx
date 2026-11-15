import Link from "next/link";

export const metadata = {
  title: "404 Not Found · VEAP Assurance Platform",
  description: "Requested page not found",
};

export default function NotFound() {
  return (
    <main
      style={{
        padding: "4rem 2rem",
        textAlign: "center",
        fontFamily: "system-ui, sans-serif",
        background: "#101a24",
        color: "#eef4f8",
        minHeight: "100vh",
      }}
    >
      <h1>404 · Page Not Found</h1>
      <p style={{ color: "#94a3b8", maxWidth: "32rem", margin: "1rem auto 2rem" }}>
        The requested resource was not found on this VEAP host. Use the links below to return to verified dashboards.
      </p>
      <nav>
        <Link href="/" style={{ color: "#38bdf8", marginRight: "1.5rem" }}>
          Observatory
        </Link>
        <Link href="/studio" style={{ color: "#38bdf8", marginRight: "1.5rem" }}>
          Assurance Studio
        </Link>
        <Link href="/replay" style={{ color: "#38bdf8" }}>
          Native Replay
        </Link>
      </nav>
    </main>
  );
}

