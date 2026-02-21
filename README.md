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
