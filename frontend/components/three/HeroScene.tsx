"use client";

import { Suspense, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, MeshDistortMaterial, Sparkles } from "@react-three/drei";
import * as THREE from "three";

function MuseumPedestalSculpture() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.25;
      meshRef.current.rotation.x = Math.sin(state.clock.getElapsedTime() * 0.5) * 0.15;
    }
  });

  return (
    <group position={[0, -0.2, 0]}>
      {/* Museum Pedestal */}
      <mesh position={[0, -1.8, 0]}>
        <cylinderGeometry args={[1.2, 1.4, 1.2, 32]} />
        <meshStandardMaterial color="#18181b" roughness={0.3} metalness={0.8} />
      </mesh>
      <mesh position={[0, -1.18, 0]}>
        <cylinderGeometry args={[1.25, 1.25, 0.08, 32]} />
        <meshStandardMaterial color="#fbbf24" roughness={0.2} metalness={0.9} />
      </mesh>

      {/* Floating Centerpiece Sculpture */}
      <Float speed={1.8} rotationIntensity={0.5} floatIntensity={0.5}>
        <mesh ref={meshRef} position={[0, 0.2, 0]}>
          <torusKnotGeometry args={[0.7, 0.24, 128, 32]} />
          <MeshDistortMaterial
            color="#fbbf24"
            attach="material"
            distort={0.2}
            speed={1.5}
            roughness={0.25}
            metalness={0.85}
          />
        </mesh>
      </Float>

      {/* Ambient Museum Sparkles */}
      <Sparkles count={35} scale={4} size={2.5} speed={0.4} color="#fef08a" />
    </group>
  );
}

export function HeroScene() {
  return (
    <div className="absolute inset-0 -z-10 opacity-60">
      <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
        <ambientLight intensity={0.6} />
        <spotLight position={[5, 8, 5]} angle={0.4} penumbra={1} intensity={1.5} color="#fffbeb" />
        <directionalLight position={[-5, 5, -2]} intensity={0.5} color="#fbbf24" />
        <Suspense fallback={null}>
          <MuseumPedestalSculpture />
        </Suspense>
      </Canvas>
    </div>
  );
}
