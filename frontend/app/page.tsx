import Link from "next/link";
import { getArtifacts } from "@/lib/api";

export const dynamic = "force-dynamic";
import { Button } from "@/components/ui/button";
import { ArtifactCard } from "@/components/artifact/ArtifactCard";
import { HeroScene } from "@/components/three/HeroScene";
import { HomeHero } from "@/components/museum/HomeHero";

export default async function HomePage() {
  const { artifacts } = await getArtifacts({ limit: "8" });
  const featured = artifacts.slice(0, 4);

  return (
    <>
      <section className="relative flex min-h-[90vh] items-center overflow-hidden pt-16">
        <HeroScene />
        <div className="museum-grid absolute inset-0 opacity-20" />
        <div className="relative mx-auto max-w-7xl px-6 py-24">
          <HomeHero />
          <div className="mt-10 flex flex-wrap gap-4">
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
