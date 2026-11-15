import Script from "next/script";
import Workspace from "../components/observatory/Workspace";
export const metadata = { title: "VEAP Observatory" };
export default function Page() {
  return (
    <>
      <link rel="stylesheet" href="/observatory/style.css" />
      <Workspace />
      <Script src="/observatory/app.js" strategy="afterInteractive" />
    </>
  );
}
