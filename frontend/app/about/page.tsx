export default function AboutPage() {
  return (
    <div className="mx-auto max-w-3xl px-6 pb-24 pt-28">
      <p className="text-sm uppercase tracking-[0.2em] text-accent">About</p>
      <h1 className="mt-2 font-display text-4xl font-medium">The AI Museum Guide Project</h1>
      <div className="prose prose-invert mt-8 space-y-6 text-muted-foreground">
        <p>
          This digital museum demonstrates a multimodal AI guide that combines computer vision,
          traditional NLP, information retrieval, structured knowledge querying, extractive factoid QA,
          dialogue management, and GroqCloud-based natural-language generation.
        </p>
        <h2 className="font-display text-xl text-foreground">Architecture</h2>
        <p>
          Local NLP/IR performs tokenization, intent classification, entity extraction, slot filling,
          dialogue state tracking, SQLite querying, BM25/TF-IDF retrieval, and factoid extraction.
          GroqCloud is used only for visual artifact identification and final response generation
          from verified facts.
        </p>
        <h2 className="font-display text-xl text-foreground">Source Grounding</h2>
        <p>
          Every knowledge-based answer cites actual museum database records or retrieved document
          passages. The system never invents metadata or sources.
        </p>
      </div>
    </div>
  );
}
