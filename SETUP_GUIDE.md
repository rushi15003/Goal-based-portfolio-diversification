# 🚀 Goal-Based Portfolio Allocation System - Setup Guide

Complete guide to set up and run the Goal-Based Portfolio Allocation System on your local machine.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Node.js 16+** - [Download here](https://nodejs.org/)
- **MongoDB Atlas Account** (Free) - [Sign up here](https://www.mongodb.com/cloud/atlas/register)
- **Git** - [Download here](https://git-scm.com/)

---

## 🗄️ Part 1: MongoDB Atlas Setup

### Step 1: Create MongoDB Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) and sign up
2. Log in to your account

### Step 2: Create a Free Cluster
1. Click **"Create"** or **"Build a Database"**
2. Select **"M0 Free"** tier
3. Choose your preferred cloud provider and region
4. Name your cluster (e.g., `portfolio-cluster`)
5. Click **"Create Deployment"**

### Step 3: Create Database User
1. Create a database user with username and password
2. **Save your credentials safely** - you'll need them soon

### Step 4: Configure Network Access
1. Click **"Network Access"** in the left sidebar
2. Click **"Add IP Address"**
3. Select **"Allow Access from Anywhere"** (0.0.0.0/0) for development
4. Click **"Confirm"**

### Step 5: Get Connection String
1. Go to **"Database"** and click **"Connect"** on your cluster
2. Choose **"Connect your application"**
3. Select **Driver: Python**, **Version: 3.12 or later**
4. Copy the connection string - it looks like:
   ```
   mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
   ```

---

## 🔧 Part 2: Backend Setup

### Step 1: Navigate to Backend Directory
```bash
cd C:\Users\ASUS\Downloads\Goal-Based-Portfolio-Allocation-System-main\backend
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# On Windows CMD:
venv\Scripts\activate.bat
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create .env File
Create a file named `.env` in the `backend` directory with the following content:

```env
# Application Settings
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8000

# MongoDB Atlas Connection
# Replace <username>, <password>, and <cluster> with your actual MongoDB Atlas credentials
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB=portfolio_allocation

# Gemini API Key (Optional - for AI features)
# Get from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# CORS Settings
CORS_ORIGINS=http://localhost:5173
```

**Important**: Replace the placeholders:
- `<username>` - Your MongoDB Atlas username
- `<password>` - Your MongoDB Atlas password
- `<cluster>` - Your cluster name from the connection string

### Step 5: Start Backend Server
```bash
# Make sure you're in the backend directory with venv activated
uvicorn app.main:app --reload
```

✅ **Backend should now be running at:** http://localhost:8000

You can verify by visiting:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## 🎨 Part 3: Frontend Setup

### Step 1: Open New Terminal
Keep the backend running and open a **new terminal window**

### Step 2: Navigate to Frontend Directory
```bash
cd C:\Users\ASUS\Downloads\Goal-Based-Portfolio-Allocation-System-main\frontend\my-app
```

### Step 3: Install Node Dependencies
```bash
npm install
```

### Step 4: Create .env File (Optional)
If you're running the backend on a different port, create a `.env` file in `frontend/my-app`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Step 5: Start Frontend Development Server
```bash
npm run dev
```

✅ **Frontend should now be running at:** http://localhost:5173

---

## 🎯 Part 4: Access the Application

1. **Open your browser** and go to: http://localhost:5173
2. You should see the Goal-Based Portfolio Allocation interface
3. The frontend will communicate with the backend API automatically

---

## 📝 Quick Start Commands

### Terminal 1 - Backend
```bash
cd backend
.\venv\Scripts\Activate.ps1    # Activate virtual environment
uvicorn app.main:app --reload   # Start backend server
```

### Terminal 2 - Frontend
```bash
cd frontend\my-app
npm run dev                      # Start frontend server
```

---

## 🔍 Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError`
- **Solution**: Make sure virtual environment is activated and dependencies are installed
  ```bash
  pip install -r requirements.txt
  ```

**Problem**: MongoDB connection error
- **Solution**: 
  - Verify your `.env` file has correct MongoDB URI
  - Check MongoDB Atlas network access allows your IP
  - Ensure username/password are URL-encoded (no special characters unescaped)

**Problem**: Port 8000 already in use
- **Solution**: Stop other applications using port 8000, or change the port in `.env`:
  ```env
  API_PORT=8001
  ```

### Frontend Issues

**Problem**: `npm install` fails
- **Solution**: 
  - Clear npm cache: `npm cache clean --force`
  - Delete `node_modules` and `package-lock.json`, then run `npm install` again

**Problem**: Can't connect to backend
- **Solution**: 
  - Verify backend is running at http://localhost:8000
  - Check CORS settings in backend `.env` file includes `http://localhost:5173`

**Problem**: Port 5173 already in use
- **Solution**: Vite will automatically use the next available port (5174, 5175, etc.)

---

## 🛠️ Additional Commands

### Backend Commands
```bash
# Run with specific host/port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run without auto-reload (production mode)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Commands
```bash
# Development mode
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

---

## 📚 Project Structure

```
Goal-Based-Portfolio-Allocation-System/
├── backend/
│   ├── app/
│   │   ├── core/          # Configuration and settings
│   │   ├── db/            # Database connection
│   │   ├── routers/       # API endpoints
│   │   ├── schemas/       # Pydantic models
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Environment variables
├── frontend/
│   └── my-app/
│       ├── src/
│       │   ├── api/       # API client
│       │   ├── pages/     # React components
│       │   └── main.jsx   # Entry point
│       ├── package.json   # Node dependencies
│       └── .env          # Frontend environment variables
└── SETUP_GUIDE.md        # This file
```

---

## 🎉 Next Steps

Once everything is running:

1. **Test the Health Endpoint**: Visit http://localhost:8000/docs
2. **Explore the API Documentation**: FastAPI provides interactive docs
3. **Use the Application**: Go to http://localhost:5173 and start using the portfolio allocation system

---

## 📞 Need Help?

If you encounter any issues:
1. Check the terminal output for error messages
2. Verify all prerequisites are installed
3. Ensure MongoDB Atlas is properly configured
4. Double-check your `.env` files

---

## 🔒 Security Notes

⚠️ **For Production**:
- Change MongoDB Network Access from "Anywhere" to specific IPs
- Use strong, unique passwords
- Keep `.env` files out of version control (already in `.gitignore`)
- Use environment-specific configuration
- Enable HTTPS for production deployments

---

**Happy Coding! 🚀**





