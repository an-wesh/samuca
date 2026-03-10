# AI Trading Bot Builder

## Deployment Architecture
- **Frontend**: Vercel (React)
- **Backend**: Render (FastAPI)
- **Database**: MongoDB Atlas (Free)

## Quick Links
- Frontend: `https://your-app.vercel.app`
- Backend API: `https://your-api.onrender.com`

---

## Deployment Guide

### Prerequisites
1. GitHub account with code pushed
2. MongoDB Atlas account (free)
3. Vercel account (free)
4. Render account (free)

### Step 1: MongoDB Atlas Setup
See detailed instructions below.

### Step 2: Deploy Backend to Render
See detailed instructions below.

### Step 3: Deploy Frontend to Vercel
See detailed instructions below.

---

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8001

# Frontend  
cd frontend
yarn install
yarn start
```

## Test Credentials
- Email: admin@test.com
- Password: admin123

- {
  "env_image_name": "fastapi_react_mongo_shadcn_base_image_cloud_arm:release-11022026-1",
  "job_id": "93f483a6-b57b-4108-bf40-e50dd2f6c352",
  "created_at": "2026-02-22T10:28:28.261155+00:00Z"
}
