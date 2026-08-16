"use client";

import { Suspense, useEffect, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { ParticleSphere } from "@/components/ui/cosmos-3d-orbit-gallery";

interface CosmosOrbitSceneProps {
  images: string[];
}

export function CosmosOrbitScene({ images }: CosmosOrbitSceneProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || !images || images.length === 0) {
    return null;
  }

  return (
    <div className="absolute inset-0 -z-10 h-full w-full opacity-70 pointer-events-auto">
      <Canvas camera={{ position: [-10, 0, 10], fov: 50 }}>
        <ambientLight intensity={0.6} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <Suspense fallback={null}>
          <ParticleSphere images={images} />
        </Suspense>
        <OrbitControls enablePan={false} enableZoom={false} enableRotate={true} />
      </Canvas>
    </div>
  );
}
