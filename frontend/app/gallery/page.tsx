"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getGalleries, Gallery } from "@/lib/api";

export default function GalleryPage() {
  const [galleries, setGalleries] = useState<Gallery[]>([]);

  useEffect(() => {
    getGalleries().then((d) => setGalleries(d.galleries)).catch(() => {});
  }, []);

  return (
    <div className="mx-auto max-w-7xl px-6 pb-24 pt-28">
      <p className="text-sm uppercase tracking-[0.2em] text-accent">Galleries</p>
      <h1 className="mt-2 font-display text-4xl font-medium">Explore Our Spaces</h1>
      <div className="mt-12 grid gap-6 md:grid-cols-2">
        {galleries.map((g) => (
          <div key={g.gallery_id} className="rounded-xl border border-border bg-card p-6">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="font-display text-2xl">{g.name}</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  Floor {g.floor} · {g.location}
                </p>
              </div>
              <span className="rounded-full bg-accent/10 px-3 py-1 text-xs text-accent">
                {g.artifact_count} works
              </span>
            </div>
            <p className="mt-4 text-sm text-muted-foreground">{g.description}</p>
            {g.artifacts && g.artifacts.length > 0 && (
              <ul className="mt-4 space-y-1 text-sm">
                {g.artifacts.slice(0, 4).map((a) => (
                  <li key={a.artifact_id}>
                    <Link href={`/collection/${a.artifact_id}`} className="hover:text-accent">
                      {a.name}
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
