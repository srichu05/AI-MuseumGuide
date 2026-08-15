import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="border-t border-border/60 bg-card/50 py-12">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-6 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="font-display text-lg">Digital Museum</p>
          <p className="mt-1 text-sm text-muted-foreground">
            NLP/IR-powered museum guide with grounded conversational QA
          </p>
        </div>
        <div className="flex gap-6 text-sm text-muted-foreground">
          <Link href="/about" className="hover:text-accent">About the Project</Link>
          <Link href="/guide" className="hover:text-accent">AI Guide</Link>
          <Link href="/collection" className="hover:text-accent">Collection</Link>
        </div>
      </div>
    </footer>
  );
}
