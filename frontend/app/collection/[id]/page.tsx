export const dynamic = "force-dynamic";

import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getArtifact, getArtifactImage } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ArtifactCard } from "@/components/artifact/ArtifactCard";

export default async function ArtifactDetailPage({ params }: { params: { id: string } }) {
  let data;
  try {
    data = await getArtifact(params.id);
  } catch {
    notFound();
  }
  const { artifact, exhibitions, related_works } = data;

  return (
    <div className="mx-auto max-w-7xl px-6 pb-24 pt-28">
      <div className="grid gap-12 lg:grid-cols-2">
        <div className="relative aspect-[4/5] overflow-hidden rounded-xl border border-border">
          <Image
            src={getArtifactImage(artifact)}
            alt={artifact.name}
            fill
            className="object-cover"
            priority
          />
        </div>
        <div>
          <p className="text-sm uppercase tracking-wider text-accent">{artifact.type}</p>
          <h1 className="mt-2 font-display text-4xl font-medium md:text-5xl">{artifact.name}</h1>
          <p className="mt-4 text-xl text-muted-foreground">{artifact.artist_name}</p>
          <dl className="mt-8 grid grid-cols-2 gap-4 text-sm">
            <div><dt className="text-muted-foreground">Year</dt><dd className="mt-1 font-medium">{artifact.year}</dd></div>
            <div><dt className="text-muted-foreground">Period</dt><dd className="mt-1 font-medium">{artifact.period_name}</dd></div>
            <div><dt className="text-muted-foreground">Gallery</dt><dd className="mt-1 font-medium">{artifact.gallery_name}</dd></div>
            <div><dt className="text-muted-foreground">Floor</dt><dd className="mt-1 font-medium">{artifact.floor}</dd></div>
          </dl>
          <p className="mt-8 leading-relaxed text-muted-foreground">{artifact.description}</p>
          <Button asChild className="mt-8" size="lg">
            <Link href={`/guide?artifact=${artifact.artifact_id}`}>Ask Museum AI</Link>
          </Button>
        </div>
      </div>

      {exhibitions.length > 0 && (
        <section className="mt-20">
          <h2 className="font-display text-2xl">Exhibitions</h2>
          <ul className="mt-4 space-y-3">
            {exhibitions.map((e) => (
              <li key={e.exhibition_id} className="rounded-lg border border-border bg-card p-4">
                <p className="font-medium">{e.name}</p>
                <p className="text-sm text-muted-foreground">{e.start_date} — {e.end_date}</p>
              </li>
            ))}
          </ul>
        </section>
      )}

      {related_works.length > 0 && (
        <section className="mt-20">
          <h2 className="font-display text-2xl">Related Works</h2>
          <div className="mt-6 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {related_works.slice(0, 4).map((a) => (
              <ArtifactCard key={a.artifact_id} artifact={a} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
