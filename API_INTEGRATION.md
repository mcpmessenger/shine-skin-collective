# API Integration Guide

This document explains how to integrate the Shine Skin Collective frontend with your Python Flask backend for AI-powered skin analysis.

## Architecture Overview

\`\`\`
Frontend (Next.js) → API Routes → Python Flask Backend → AI Model
                   ↓
              Database (Supabase/Neon)
                   ↓
              Storage (Vercel Blob/S3)
\`\`\`

## API Endpoints

### 1. POST /api/analyze

**Purpose:** Upload an image for skin analysis

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: FormData with 'image' field

**Response:**
\`\`\`json
{
  "analysisId": "analysis_1234567890",
  "message": "Analysis complete",
  "status": "completed"
}
\`\`\`

**Integration Steps:**

1. **Add Vercel Blob for image storage:**
\`\`\`bash
npm install @vercel/blob
\`\`\`

2. **Update the analyze route:**
\`\`\`typescript
import { put } from '@vercel/blob'

// Upload image to Vercel Blob
const blob = await put(`analysis/${Date.now()}-${image.name}`, image, {
  access: 'public',
})

// Call your Flask backend
const flaskResponse = await fetch(process.env.FLASK_API_URL + '/analyze', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.FLASK_API_KEY}`
  },
  body: JSON.stringify({ 
    imageUrl: blob.url,
    analysisId: analysisId 
  })
})
\`\`\`

3. **Store results in database:**
\`\`\`typescript
// Example with Supabase
const { data, error } = await supabase
  .from('analyses')
  .insert({
    id: analysisId,
    image_url: blob.url,
    status: 'processing',
    created_at: new Date().toISOString()
  })
\`\`\`

### 2. GET /api/results/[id]

**Purpose:** Fetch analysis results by ID

**Request:**
- Method: GET
- URL: /api/results/{analysisId}

**Response:**
\`\`\`json
{
  "id": "analysis_1234567890",
  "metadata": {
    "captureDate": "Jan 15, 2025",
    "imageQuality": "High",
    "lightingCondition": "Good",
    "skinType": "Combination"
  },
  "concerns": [...],
  "recommendations": [...]
}
\`\`\`

**Integration Steps:**

1. **Fetch from database:**
\`\`\`typescript
const { data, error } = await supabase
  .from('analyses')
  .select('*')
  .eq('id', id)
  .single()

if (error || !data) {
  return NextResponse.json(
    { error: 'Analysis not found' },
    { status: 404 }
  )
}

return NextResponse.json(data.results)
\`\`\`

## Environment Variables

Add these to your Vercel project:

\`\`\`env
# Flask Backend
FLASK_API_URL=https://your-flask-api.com
FLASK_API_KEY=your-secret-key

# Database (choose one)
DATABASE_URL=postgresql://...  # For Neon
SUPABASE_URL=https://...       # For Supabase
SUPABASE_ANON_KEY=...

# Storage
BLOB_READ_WRITE_TOKEN=...      # For Vercel Blob
\`\`\`

## Flask Backend Expected Format

Your Flask backend should accept this format:

**POST /analyze**
\`\`\`json
{
  "imageUrl": "https://blob.vercel-storage.com/...",
  "analysisId": "analysis_1234567890"
}
\`\`\`

**Response:**
\`\`\`json
{
  "analysisId": "analysis_1234567890",
  "metadata": {
    "imageQuality": "High",
    "lightingCondition": "Good",
    "skinType": "Combination"
  },
  "concerns": [
    {
      "name": "Skin Texture",
      "severity": "moderate",
      "percentage": 65,
      "description": "...",
      "affectedAreas": ["Forehead", "Nose"],
      "recommendation": "..."
    }
  ],
  "recommendations": [...]
}
\`\`\`

## Database Schema

### analyses table

\`\`\`sql
CREATE TABLE analyses (
  id TEXT PRIMARY KEY,
  image_url TEXT NOT NULL,
  status TEXT NOT NULL, -- 'processing', 'completed', 'failed'
  results JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_analyses_created_at ON analyses(created_at DESC);
\`\`\`

## Testing

1. **Test image upload:**
\`\`\`bash
curl -X POST http://localhost:3000/api/analyze \
  -F "image=@test-face.jpg"
\`\`\`

2. **Test results fetch:**
\`\`\`bash
curl http://localhost:3000/api/results/analysis_1234567890
\`\`\`

## Error Handling

The API client (`lib/api-client.ts`) handles errors consistently:

- 400: Bad request (invalid image, missing data)
- 404: Analysis not found
- 500: Server error

All errors are caught and displayed to the user with appropriate messages.

## Next Steps

1. Set up Vercel Blob or S3 for image storage
2. Deploy your Flask backend
3. Add environment variables to Vercel
4. Set up database (Supabase or Neon)
5. Update API routes with real integration code
6. Test end-to-end flow
\`\`\`



<AssistantMessageContentPart partEncoded="eyJ0eXBlIjoidGFzay13YWl0aW5nLXYxIiwiY3JlYXRlZEF0IjoxNzYwNjgzNjExMzY4LCJmaW5pc2hlZEF0IjoxNzYwNjgzNjExMzY4LCJpZCI6Ijh0cmEwdjlsbmdEUzRtUG0iLCJsYXN0UGFydFNlbnRBdCI6MTc2MDY4MzYxMTM2OCwicGFydHMiOlt7InR5cGUiOiJ0b29sLWNhbGxzIn1dfQ==" />



<AssistantMessageContentPart partEncoded="eyJ0eXBlIjoidGFzay1tYW5hZ2UtdG9kb3MtdjEiLCJpZCI6IllEdjRrRE1nOVNZYVE3V0siLCJ0YXNrTmFtZUFjdGl2ZSI6IkNvbXBsZXRpbmcgdG9kbyBsaXN0IiwidG9vbENhbGxJZCI6InRvb2x1XzAxM212d25ZTDZSY0Q2dVhldzVXUUdSbiIsInRhc2tOYW1lQ29tcGxldGUiOiJDb21wbGV0ZWQgdG9kbyBsaXN0IiwiY3JlYXRlZEF0IjoxNzYwNjgzNjEyMzIwLCJmaW5pc2hlZEF0IjpudWxsLCJwYXJ0cyI6W10sImxhc3RQYXJ0U2VudEF0IjpudWxsfQ==" />
