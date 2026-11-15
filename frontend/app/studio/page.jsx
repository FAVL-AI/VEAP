import Script from "next/script";
import Workspace from "../../components/studio/Workspace";
export const metadata = { title: "VEAP Assurance Studio" };
export default function Page() {
  return (
    <>
      <link rel="stylesheet" href="/studio/style.css" />
      <Workspace />
      <Script src="/studio/app.js" strategy="afterInteractive" />
    </>
  );
}
