"use client";

import Image from "next/image";
import Link from "next/link";
import { motion } from "motion/react";
import { Artifact, getArtifactImage } from "@/lib/api";
import { cn } from "@/lib/utils";

interface ArtifactCardProps {
  artifact: Artifact;
  className?: string;
  priority?: boolean;
}

export function ArtifactCard({ artifact, className, priority }: ArtifactCardProps) {
  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ duration: 0.3 }}
      className={cn("group", className)}
    >
      <Link href={`/collection/${artifact.artifact_id}`}>
        <div className="relative aspect-[4/5] overflow-hidden rounded-lg border border-border/60 bg-muted">
          <Image
            src={getArtifactImage(artifact)}
            alt={artifact.name}
            fill
            priority={priority}
            className="object-cover transition-transform duration-500 group-hover:scale-105"
            sizes="(max-width: 768px) 100vw, 25vw"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-background/90 via-transparent to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
        </div>
        <div className="mt-4">
          <h3 className="font-display text-lg font-medium group-hover:text-accent">{artifact.name}</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            {artifact.artist_name} · {artifact.year}
          </p>
        </div>
      </Link>
    </motion.div>
  );
}
