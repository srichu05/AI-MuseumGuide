import { Suspense } from "react";
import GuidePage from "./GuideClient";

export default function Page() {
  return (
    <Suspense fallback={<div className="px-6 pt-28 text-muted-foreground">Loading guide...</div>}>
      <GuidePage />
    </Suspense>
  );
}
