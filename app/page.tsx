"use client"

import { useState, useRef, useEffect } from "react"
import { Camera, Sparkles, Loader2, Upload, Image as ImageIcon, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { uploadImageForAnalysis, ApiError } from "@/lib/api-client"

export default function CameraLandingPage() {
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [isCapturing, setIsCapturing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [detectionSupported, setDetectionSupported] = useState(false)
  const [faceDetected, setFaceDetected] = useState<boolean | null>(null)
  const [mode, setMode] = useState<'camera' | 'upload'>('camera')
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const router = useRouter()

  useEffect(() => {
    startCamera()
    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop())
      }
    }
  }, [])

  // Lightweight real-time face detection indicator (if supported by the browser)
  useEffect(() => {
    let interval: any
    const FaceDetectorCtor: any = typeof window !== 'undefined' ? (window as any).FaceDetector : undefined
    if (FaceDetectorCtor && videoRef.current) {
      setDetectionSupported(true)
      const detector = new FaceDetectorCtor({ fastMode: true, maxDetectedFaces: 1 })
      interval = setInterval(async () => {
        try {
          if (!videoRef.current) return
          const faces = await detector.detect(videoRef.current)
          setFaceDetected(Array.isArray(faces) && faces.length > 0)
        } catch {
          // If detection fails intermittently, do nothing; indicator will retry
        }
      }, 700)
    } else {
      setDetectionSupported(false)
    }
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [videoRef.current])

  const startCamera = async () => {
    try {
      // Feature detection + secure context guard
      if (typeof navigator === "undefined" || typeof window === "undefined") return
      const hasMediaDevices = typeof (navigator as any).mediaDevices !== "undefined" &&
        typeof (navigator as any).mediaDevices.getUserMedia === "function"
      if (!hasMediaDevices) {
        setError(
          window.isSecureContext
            ? "Camera not supported in this browser/device. Try uploading a photo."
            : "Camera requires a secure context (https or localhost). Please switch to https or use localhost."
        )
        return
      }

      const mediaStream = await (navigator as any).mediaDevices.getUserMedia({
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
      setError("Unable to access camera. Please grant permissions or upload a photo.")
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

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setSelectedImage(e.target?.result as string)
        setMode('upload')
      }
      reader.readAsDataURL(file)
    }
  }

  const handleUploadImage = async () => {
    if (!selectedImage) return

    setIsUploading(true)
    setError(null)

    try {
      // Convert data URL to blob
      const response = await fetch(selectedImage)
      const blob = await response.blob()
      
      const data = await uploadImageForAnalysis(blob)
      router.push(`/results?id=${data.analysisId}`)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError("Network error. Please try again.")
      }
      setIsUploading(false)
    }
  }

  const clearSelectedImage = () => {
    setSelectedImage(null)
    setMode('camera')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="relative h-screen w-full overflow-hidden bg-black">
      {/* Video Stream or Selected Image */}
      {mode === 'camera' ? (
        <video ref={videoRef} autoPlay playsInline muted className="absolute inset-0 h-full w-full object-cover" />
      ) : selectedImage ? (
        <img src={selectedImage} alt="Selected" className="absolute inset-0 h-full w-full object-cover" />
      ) : (
        <div className="absolute inset-0 bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900" />
      )}

      {/* Hidden canvas for capture */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Overlay UI */}
      <div className="absolute inset-0 flex flex-col">
        {/* Header */}
        <div className="relative z-10 flex items-center justify-between p-6">
          <div className="flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-bold text-white">Shine Skin Collective</h1>
          </div>
          
          {/* Mode Toggle */}
          <div className="flex gap-2">
            <Button
              variant={mode === 'camera' ? 'default' : 'outline'}
              size="sm"
              onClick={() => {
                setMode('camera')
                setSelectedImage(null)
                if (fileInputRef.current) fileInputRef.current.value = ''
              }}
              className="text-white"
            >
              <Camera className="h-4 w-4 mr-2" />
              Camera
            </Button>
            <Button
              variant={mode === 'upload' ? 'default' : 'outline'}
              size="sm"
              onClick={() => {
                setMode('upload')
                fileInputRef.current?.click()
              }}
              className="text-white"
            >
              <Upload className="h-4 w-4 mr-2" />
              Upload
            </Button>
          </div>
        </div>

        {/* Center Guide */}
        <div className="flex flex-1 items-center justify-center p-6">
          <div className="relative">
            {mode === 'camera' ? (
              <>
                {/* Face guide overlay for camera */}
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
              </>
            ) : mode === 'upload' && !selectedImage ? (
              <>
                {/* Upload area */}
                <div className="relative h-80 w-80 rounded-full border-4 border-dashed border-primary/50 shadow-[0_0_40px_rgba(168,85,247,0.3)] flex items-center justify-center">
                  <div className="text-center">
                    <ImageIcon className="h-16 w-16 text-primary/70 mx-auto mb-4" />
                    <p className="text-sm font-medium text-white/90">Select a photo to analyze</p>
                  </div>
                </div>
              </>
            ) : selectedImage ? (
              <>
                {/* Selected image preview */}
                <div className="relative h-80 w-80 rounded-full border-4 border-primary/50 shadow-[0_0_40px_rgba(168,85,247,0.3)] overflow-hidden">
                  <img src={selectedImage} alt="Selected" className="h-full w-full object-cover" />
                  <button
                    onClick={clearSelectedImage}
                    className="absolute top-2 right-2 h-8 w-8 rounded-full bg-black/50 flex items-center justify-center text-white hover:bg-black/70"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </>
            ) : null}
          </div>
        </div>

        {/* Bottom Controls */}
        <div className="relative z-10 flex flex-col items-center gap-4 p-8 pb-12">
          {error && <div className="rounded-lg bg-destructive/10 px-4 py-2 text-sm text-destructive">{error}</div>}

          {mode === 'camera' && detectionSupported && (
            <div className="flex items-center gap-2 text-xs text-white/80">
              <span
                className={
                  "inline-block h-2.5 w-2.5 rounded-full " +
                  (faceDetected ? "bg-emerald-400" : "bg-red-400")
                }
              />
              <span>{faceDetected ? "Face detected" : "No face detected"}</span>
            </div>
          )}

          {mode === 'camera' ? (
            <>
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
            </>
          ) : mode === 'upload' ? (
            <>
              {!selectedImage ? (
                <>
                  <Button
                    size="lg"
                    onClick={() => fileInputRef.current?.click()}
                    className="h-20 w-20 rounded-full bg-primary p-0 shadow-lg hover:bg-primary/90"
                  >
                    <Upload className="h-8 w-8 text-white" />
                  </Button>

                  <p className="text-center text-sm text-white/70">
                    Tap to select a photo
                  </p>
                </>
              ) : (
                <>
                  <Button
                    size="lg"
                    onClick={handleUploadImage}
                    disabled={isUploading}
                    className="h-20 w-20 rounded-full bg-primary p-0 shadow-lg hover:bg-primary/90 disabled:opacity-50"
                  >
                    {isUploading ? (
                      <Loader2 className="h-8 w-8 animate-spin text-white" />
                    ) : (
                      <Sparkles className="h-8 w-8 text-white" />
                    )}
                  </Button>

                  <p className="text-center text-sm text-white/70">
                    {isUploading ? "Analyzing your skin..." : "Tap to analyze this photo"}
                  </p>
                </>
              )}
            </>
          ) : null}
        </div>
      </div>

      {/* Gradient overlays for better text visibility */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-black/60 to-transparent" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-48 bg-gradient-to-t from-black/80 to-transparent" />
    </div>
  )
}
