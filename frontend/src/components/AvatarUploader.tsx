import React from 'react';

export default function AvatarUploader() {
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const url = URL.createObjectURL(file);
      localStorage.setItem('avatarUrl', url);
      window.location.reload(); // 또는 상태 관리로 리렌더링
    }
  };

  return (
    <div style={{ margin: '1rem' }}>
      <label>
        GLB 업로드:
        <input type="file" accept=".glb" onChange={handleFileChange} />
      </label>
    </div>
  );
}
