"use client"

import { useState, useRef, useEffect } from "react"
import { Camera, Sparkles, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { uploadImageForAnalysis, ApiError } from "@/lib/api-client"

export default function CameraLandingPage() {
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [isCapturing, setIsCapturing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const router = useRouter()

  useEffect(() => {
    startCamera()
    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop())
      }
    }
  }, [])

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "user",
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
      })
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
    } catch (err) {
      setError("Unable to access camera. Please grant camera permissions.")
      console.error("Camera error:", err)
    }
  }

  const captureImage = async () => {
    if (!videoRef.current || !canvasRef.current) return

    setIsCapturing(true)
    setError(null)

    const video = videoRef.current
    const canvas = canvasRef.current
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    const ctx = canvas.getContext("2d")
    if (ctx) {
      ctx.drawImage(video, 0, 0)

      // Convert to blob
      canvas.toBlob(
        async (blob) => {
          if (blob) {
            try {
              const data = await uploadImageForAnalysis(blob)
              router.push(`/results?id=${data.analysisId}`)
            } catch (err) {
              if (err instanceof ApiError) {
                setError(err.message)
              } else {
                setError("Network error. Please try again.")
              }
              setIsCapturing(false)
            }
          }
        },
        "image/jpeg",
        0.95,
      )
    }
  }

  return (
    <div className="relative h-screen w-full overflow-hidden bg-black">
      {/* Video Stream */}
      <video ref={videoRef} autoPlay playsInline muted className="absolute inset-0 h-full w-full object-cover" />

      {/* Hidden canvas for capture */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Overlay UI */}
      <div className="absolute inset-0 flex flex-col">
        {/* Header */}
        <div className="relative z-10 flex items-center justify-between p-6">
          <div className="flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-bold text-white">Shine Skin Collective</h1>
          </div>
        </div>

        {/* Center Guide */}
        <div className="flex flex-1 items-center justify-center p-6">
          <div className="relative">
            {/* Face guide overlay */}
            <div className="relative h-80 w-80 rounded-full border-4 border-primary/50 shadow-[0_0_40px_rgba(168,85,247,0.3)]">
              <div className="absolute -left-2 -top-2 h-8 w-8 rounded-full border-4 border-primary" />
              <div className="absolute -right-2 -top-2 h-8 w-8 rounded-full border-4 border-primary" />
              <div className="absolute -bottom-2 -left-2 h-8 w-8 rounded-full border-4 border-primary" />
              <div className="absolute -bottom-2 -right-2 h-8 w-8 rounded-full border-4 border-primary" />
            </div>

            {/* Instructions */}
            {!isCapturing && (
              <div className="absolute -bottom-16 left-1/2 -translate-x-1/2 text-center">
                <p className="text-sm font-medium text-white/90">Position your face in the circle</p>
              </div>
            )}
          </div>
        </div>

        {/* Bottom Controls */}
        <div className="relative z-10 flex flex-col items-center gap-4 p-8 pb-12">
          {error && <div className="rounded-lg bg-destructive/10 px-4 py-2 text-sm text-destructive">{error}</div>}

          <Button
            size="lg"
            onClick={captureImage}
            disabled={isCapturing || !stream}
            className="h-20 w-20 rounded-full bg-primary p-0 shadow-lg hover:bg-primary/90 disabled:opacity-50"
          >
            {isCapturing ? (
              <Loader2 className="h-8 w-8 animate-spin text-white" />
            ) : (
              <Camera className="h-8 w-8 text-white" />
            )}
          </Button>

          <p className="text-center text-sm text-white/70">
            {isCapturing ? "Analyzing your skin..." : "Tap to capture and analyze"}
          </p>
        </div>
      </div>

      {/* Gradient overlays for better text visibility */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-black/60 to-transparent" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-48 bg-gradient-to-t from-black/80 to-transparent" />
    </div>
  )
}
