"use client";

import { useCallback, useRef, useState } from "react";
import Image from "next/image";
import { Upload, Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { identifyArtifact, Artifact, IdentifyResponse } from "@/lib/api";
import { cn } from "@/lib/utils";

interface ImageUploadProps {
  onIdentified: (result: IdentifyResponse) => void;
  sessionId?: string;
  className?: string;
}

export function ImageUpload({ onIdentified, sessionId, className }: ImageUploadProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const [artifact, setArtifact] = useState<Artifact | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(
    async (file: File) => {
      if (!file.type.startsWith("image/")) {
        setStatus("error");
        setMessage("Please upload a valid image file.");
        return;
      }
      setPreview(URL.createObjectURL(file));
      setStatus("uploading");
      setMessage("Analyzing artwork...");
      try {
        const result = await identifyArtifact(file, sessionId);
        if (result.status === "identified" && result.artifact) {
          setStatus("success");
          setArtifact(result.artifact);
          setMessage(`Identified: ${result.artifact.name}`);
          onIdentified(result);
        } else {
          setStatus("error");
          setMessage(result.message || "Could not identify artifact.");
          onIdentified(result);
        }
      } catch {
        setStatus("error");
        setMessage("Identification failed. Please try again.");
      }
    },
    [onIdentified, sessionId]
  );

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div className={cn("space-y-4", className)}>
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        className={cn(
          "relative flex min-h-[200px] cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-border/80 bg-muted/30 p-8 transition-colors hover:border-accent/50 hover:bg-muted/50",
          status === "uploading" && "pointer-events-none opacity-70"
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />
        {preview ? (
          <div className="relative h-40 w-full max-w-xs">
            <Image src={preview} alt="Upload preview" fill className="rounded-lg object-cover" />
          </div>
        ) : (
          <>
            <Upload className="mb-3 h-10 w-10 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Drag & drop or click to upload an artifact image</p>
          </>
        )}
      </div>
      {status !== "idle" && (
        <div
          className={cn(
            "flex items-center gap-2 rounded-lg px-4 py-3 text-sm",
            status === "uploading" && "bg-muted text-muted-foreground",
            status === "success" && "bg-accent/10 text-accent",
            status === "error" && "bg-red-500/10 text-red-400"
          )}
        >
          {status === "uploading" && <Loader2 className="h-4 w-4 animate-spin" />}
          {status === "success" && <CheckCircle2 className="h-4 w-4" />}
          {status === "error" && <AlertCircle className="h-4 w-4" />}
          {message}
        </div>
      )}
      {artifact && (
        <div className="rounded-lg border border-border bg-card p-4">
          <p className="text-xs uppercase tracking-wider text-muted-foreground">Recognized Artifact</p>
          <p className="mt-1 font-display text-xl">{artifact.name}</p>
          <p className="text-sm text-muted-foreground">{artifact.artist_name} · {artifact.year}</p>
        </div>
      )}
    </div>
  );
}
