import React, { useEffect, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, useGLTF } from '@react-three/drei';

function CharacterModel({ avatarUrl }: { avatarUrl: string }) {
  const gltf = useGLTF(avatarUrl);
  const modelRef = useRef<any>(null);

  useFrame(() => {
    if (modelRef.current) {
      modelRef.current.rotation.y += 0.003;
    }
  });

  return (
    <primitive
      object={gltf.scene}
      ref={modelRef}
      scale={2}
      position={[0, -1, 0]}
    />
  );
}

export default function CharacterCanvas() {
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);

  useEffect(() => {
    const url = localStorage.getItem('avatarUrl');
    if (url) {
      // 파일이 실제로 존재하는지 확인
      fetch(url, { method: 'HEAD' })
        .then(res => {
          if (res.ok) setAvatarUrl(url);
        })
        .catch(() => setAvatarUrl(null));
    }
  }, []);

  return (
    <Canvas camera={{ position: [0, 1, 4] }}>
      <ambientLight intensity={0.8} />
      <directionalLight position={[2, 2, 2]} />
      {avatarUrl ? (
        <React.Suspense fallback={null}>
          <CharacterModel avatarUrl={avatarUrl} />
        </React.Suspense>
      ) : (
        <mesh>
          <boxGeometry />
          <meshStandardMaterial color="gray" />
        </mesh>
      )}
      <OrbitControls enableZoom={false} />
    </Canvas>
  );
}
