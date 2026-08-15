"use client";

import { useEffect, useState } from "react";
import { ArtifactCard } from "@/components/artifact/ArtifactCard";
import { Input } from "@/components/ui/input";
import { getArtifacts, Artifact } from "@/lib/api";
import { Search } from "lucide-react";

export default function CollectionPage() {
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [search, setSearch] = useState("");
  const [selectedType, setSelectedType] = useState<string>("All");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const params: Record<string, string> = { limit: "100" };
    if (search) params.search = search;
    if (selectedType !== "All") params.type = selectedType;

    getArtifacts(params)
      .then((d) => setArtifacts(d.artifacts))
      .catch(() => setArtifacts([]))
      .finally(() => setLoading(false));
  }, [search, selectedType]);

  const types = ["All", "Painting", "Sculpture", "Drawing"];

  return (
    <div className="mx-auto max-w-7xl px-6 pb-24 pt-28">
      <div className="mb-12">
        <p className="text-sm uppercase tracking-[0.2em] text-amber-400">The Collection</p>
        <h1 className="mt-2 font-serif text-4xl font-medium text-white">Explore Artifacts</h1>
        <p className="mt-2 max-w-xl text-zinc-400">
          Browse {artifacts.length} curated works spanning ancient civilizations to contemporary art.
        </p>
      </div>

      <div className="mb-10 flex flex-wrap items-center justify-between gap-4">
        <div className="relative w-full max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
          <Input
            className="pl-10 bg-zinc-900 border-zinc-800 text-white placeholder:text-zinc-500"
            placeholder="Search artifacts, artists..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2">
          {types.map((t) => (
            <button
              key={t}
              onClick={() => setSelectedType(t)}
              className={`px-4 py-1.5 rounded-full text-xs font-medium transition-all ${
                selectedType === t
                  ? "bg-amber-400 text-black shadow-md shadow-amber-400/20"
                  : "bg-zinc-900 text-zinc-400 hover:text-white hover:bg-zinc-800 border border-zinc-800"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-80 rounded-xl bg-zinc-900/50 animate-pulse border border-zinc-800" />
          ))}
        </div>
      ) : (
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {artifacts.map((a) => (
            <ArtifactCard key={a.artifact_id} artifact={a} />
          ))}
        </div>
      )}
    </div>
  );
}
