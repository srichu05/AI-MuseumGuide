import Link from "next/link";
import { getArtifacts, getArtifactImage } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ArtifactCard } from "@/components/artifact/ArtifactCard";
import { CosmosOrbitScene } from "@/components/three/CosmosOrbitScene";
import { HomeHero } from "@/components/museum/HomeHero";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const data = await getArtifacts({ limit: "24" }).catch(() => ({ artifacts: [], count: 0 }));
  const artifacts = data.artifacts || [];

  // Use actual museum collection images loaded from API or local fallback artifact paths
  const collectionImages =
    artifacts.length > 0
      ? artifacts.map((a) => getArtifactImage(a))
      : Array.from({ length: 24 }, (_, i) => `/artifacts/ART${String(i + 1).padStart(3, "0")}.jpg`);

  const featured = artifacts.slice(0, 4);

  return (
    <>
      <section className="relative flex min-h-[92vh] flex-col justify-between overflow-hidden pt-20 pb-12">
        <CosmosOrbitScene images={collectionImages} />
        <div className="museum-grid absolute inset-0 opacity-20 pointer-events-none" />
        
        {/* Top Text Content - Positioned Above Circling Images */}
        <div className="relative z-10 mx-auto w-full max-w-7xl px-6 pt-2 pointer-events-auto">
          <HomeHero />
        </div>

        {/* Bottom Action Buttons - Positioned Below Circling Images */}
        <div className="relative z-10 mx-auto w-full max-w-7xl px-6 pb-4 pointer-events-auto mt-28 md:mt-36">
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Button asChild size="lg">
              <Link href="/collection">Explore Collection</Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/guide">Identify an Artifact</Link>
            </Button>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-24">
        <div className="mb-12 flex items-end justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-accent">Featured Works</p>
            <h2 className="mt-2 font-display text-4xl font-medium">Masterpieces</h2>
          </div>
          <Link href="/collection" className="text-sm text-muted-foreground hover:text-accent">
            View all →
          </Link>
        </div>
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {featured.map((a, i) => (
            <ArtifactCard key={a.artifact_id} artifact={a} priority={i < 2} />
          ))}
        </div>
      </section>

      <section className="border-y border-border/60 bg-card/30 py-24">
        <div className="mx-auto max-w-7xl px-6 text-center">
          <p className="text-sm uppercase tracking-[0.2em] text-accent">AI Museum Guide</p>
          <h2 className="mt-4 font-display text-3xl md:text-4xl">
            Visual Recognition &amp; Grounded Conversational QA
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
            Upload an artwork image for identification, then ask questions answered through local NLP,
            SQLite queries, BM25 retrieval, and factoid extraction — with natural responses generated
            only from verified museum sources.
          </p>
          <Button asChild className="mt-8" size="lg">
            <Link href="/guide">Ask the Museum Guide</Link>
          </Button>
        </div>
      </section>
    </>
  );
}
