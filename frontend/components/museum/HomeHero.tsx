"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";

export function HomeHero() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current) return;
    const ctx = gsap.context(() => {
      gsap.from(".hero-line", { y: 40, opacity: 0, duration: 1, stagger: 0.15, ease: "power3.out" });
    }, ref);
    return () => ctx.revert();
  }, []);

  return (
    <div ref={ref}>
      <p className="hero-line text-sm uppercase tracking-[0.25em] text-accent">Curated Collection</p>
      <h1 className="hero-line mt-4 max-w-3xl font-display text-5xl font-medium leading-tight md:text-7xl">
        Where Art Meets <span className="gradient-text">Intelligent Discovery</span>
      </h1>
      <p className="hero-line mt-6 max-w-xl text-lg text-muted-foreground">
        A cinematic digital museum experience powered by traditional NLP, information retrieval,
        and multimodal AI — never a generic chatbot.
      </p>
    </div>
  );
}
