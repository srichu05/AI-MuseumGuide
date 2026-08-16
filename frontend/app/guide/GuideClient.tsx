"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { ImageUpload } from "@/components/upload/ImageUpload";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { IdentifyResponse, Artifact } from "@/lib/api";

export default function GuidePage() {
  const searchParams = useSearchParams();
  const [sessionId, setSessionId] = useState<string>();
  const [artifact, setArtifact] = useState<Artifact | null>(null);
  useEffect(() => {
    const artParam = searchParams.get("artifact") || searchParams.get("artifact_id");
    if (artParam) {
      import("@/lib/api").then(({ getArtifact }) => {
        getArtifact(artParam)
          .then((res) => {
            if (res.artifact) {
              setArtifact(res.artifact);
            }
          })
          .catch(() => {});
      });
    }
  }, [searchParams]);

  const handleIdentified = (result: IdentifyResponse) => {
    if (result.session_id) setSessionId(result.session_id);
    if (result.artifact) setArtifact(result.artifact);
  };

  return (
    <div className="mx-auto max-w-7xl px-6 pb-24 pt-28">
      <div className="mb-12 max-w-2xl">
        <p className="text-sm uppercase tracking-[0.2em] text-accent">AI Museum Guide</p>
        <h1 className="mt-2 font-display text-4xl font-medium">Identify &amp; Ask</h1>
        <p className="mt-4 text-muted-foreground">
          Upload an artifact image for visual identification, then ask questions processed by our
          local NLP pipeline with answers grounded in SQLite and BM25-retrieved documents.
        </p>
      </div>
      <div className="grid gap-8 lg:grid-cols-2">
        <div>
          <h2 className="mb-4 font-display text-xl">Visual Identification</h2>
          <ImageUpload sessionId={sessionId} onIdentified={handleIdentified} />
        </div>
        <div>
          <h2 className="mb-4 font-display text-xl">Conversational QA</h2>
          <ChatPanel sessionId={sessionId} artifact={artifact} className="min-h-[520px]" />
        </div>
      </div>
    </div>
  );
}
