import { useRef, useState } from "react";

import { ApiError, uploadImage, uploadVideo } from "../api/client";
import type { InferenceResponse } from "../types/detection";

interface UploadPanelProps {
  onResult: (result: InferenceResponse) => void;
}

export function UploadPanel({ onResult }: UploadPanelProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    setError(null);
    setIsUploading(true);

    try {
      const isVideo = file.type.startsWith("video/");
      const result = isVideo ? await uploadVideo(file) : await uploadImage(file);
      onResult(result);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Upload failed.";
      setError(message);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  return (
    <section className="card upload-panel">
      <h2>Upload media</h2>
      <p className="upload-hint">
        Upload an image or a short video clip to run safety detection immediately. Every detection
        is stored and appears in the history table and charts below.
      </p>
      <label className="upload-dropzone">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*,video/*"
          onChange={handleFileChange}
          disabled={isUploading}
        />
        <span>{isUploading ? "Processing..." : "Click to select an image or video"}</span>
      </label>
      {error && <p className="error-text">{error}</p>}
    </section>
  );
}
