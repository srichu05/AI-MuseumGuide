"use client";

import { useCallback, useRef, useState } from "react";
import Image from "next/image";
import { Upload, Loader2, CheckCircle2, AlertCircle, Cpu, Sparkles } from "lucide-react";
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
  const [identifyResult, setIdentifyResult] = useState<IdentifyResponse | null>(null);
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
      setMessage("Analyzing artwork with Vision Router...");
      setArtifact(null);
      setIdentifyResult(null);

      try {
        const result: IdentifyResponse = await identifyArtifact(file, sessionId);
        setIdentifyResult(result);

        if (result.status === "identified" && result.artifact) {
          setStatus("success");
          setArtifact(result.artifact);
          setMessage(`Identified Artifact: ${result.artifact.name}`);
          onIdentified(result);
        } else if (result.predicted_style) {
          setStatus("success");
          setArtifact(null);
          setMessage(`Classified Art Style: ${result.predicted_style}`);
          onIdentified(result);
        } else {
          setStatus("error");
          setMessage(result.message || "Could not recognize or classify image.");
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

  const recognitionSource = identifyResult?.recognition_source || identifyResult?.identification?.recognition_source;
  const confidence = identifyResult?.confidence ?? null;

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
          <div className="relative h-44 w-full max-w-xs">
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
            "flex flex-col gap-2 rounded-lg px-4 py-3 text-sm",
            status === "uploading" && "bg-muted text-muted-foreground",
            status === "success" && "bg-accent/10 text-accent border border-accent/20",
            status === "error" && "bg-red-500/10 text-red-400 border border-red-500/20"
          )}
        >
          <div className="flex items-center gap-2">
            {status === "uploading" && <Loader2 className="h-4 w-4 animate-spin text-accent" />}
            {status === "success" && <CheckCircle2 className="h-4 w-4 text-accent" />}
            {status === "error" && <AlertCircle className="h-4 w-4 text-red-400" />}
            <span className="font-medium">{message}</span>
          </div>

          {/* Model Source Badge */}
          {status === "success" && recognitionSource && (
            <div className="mt-1 flex items-center gap-2 text-xs">
              <span className="text-muted-foreground">Prediction Model:</span>
              {recognitionSource === "cnn" ? (
                <span className="inline-flex items-center gap-1.5 rounded-md bg-emerald-500/15 px-2.5 py-1 font-mono text-xs font-semibold text-emerald-400 border border-emerald-500/30">
                  <Cpu className="h-3.5 w-3.5 text-emerald-400" />
                  Local CNN Model {confidence !== null && `(${(confidence * 100).toFixed(1)}% confidence)`}
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 rounded-md bg-purple-500/15 px-2.5 py-1 font-mono text-xs font-semibold text-purple-300 border border-purple-500/30">
                  <Sparkles className="h-3.5 w-3.5 text-purple-300" />
                  GroqCloud Multimodal Vision (qwen3.6-27b)
                </span>
              )}
            </div>
          )}
        </div>
      )}

      {/* Recognized Database Artifact */}
      {artifact && (
        <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-xs uppercase tracking-wider text-muted-foreground">Matched Database Artifact</p>
            {recognitionSource && (
              <span className="text-[11px] font-mono uppercase text-accent/80">
                Source: {recognitionSource === "cnn" ? "Local CNN" : "Multimodal AI"}
              </span>
            )}
          </div>
          <p className="mt-1 font-display text-xl">{artifact.name}</p>
          <p className="text-sm text-muted-foreground">
            {artifact.artist_name || "Unknown Artist"} {artifact.year ? `· ${artifact.year}` : ""}
          </p>
          {artifact.description && (
            <p className="mt-2 text-xs text-muted-foreground/90 line-clamp-2">{artifact.description}</p>
          )}
        </div>
      )}

      {/* Classified Art Style (When not matched to a specific database artifact) */}
      {!artifact && identifyResult?.predicted_style && status === "success" && (
        <div className="rounded-lg border border-border/80 bg-card/60 p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-xs uppercase tracking-wider text-muted-foreground">Visual Art Style</p>
            <span className="text-[11px] font-mono text-accent">
              {recognitionSource === "cnn" ? "Local CNN Classification" : "Multimodal AI Classification"}
            </span>
          </div>
          <p className="mt-1 font-display text-xl text-accent">{identifyResult.predicted_style}</p>
          <p className="mt-1 text-xs text-muted-foreground">
            {recognitionSource === "cnn"
              ? `High-confidence prediction by local CNN classifier (${( (confidence || 0) * 100).toFixed(1)}%).`
              : "Prediction performed via GroqCloud Multimodal Vision fallback (qwen/qwen3.6-27b)."}
          </p>
        </div>
      )}
    </div>
  );
}
