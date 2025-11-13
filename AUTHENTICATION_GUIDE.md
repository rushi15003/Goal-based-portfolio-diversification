# 🔐 Authentication System Guide

Your Goal-Based Portfolio Allocation System now has a **complete authentication system** with Login and Signup pages!

---

## ✅ What's Already Implemented

### Backend (FastAPI)
- ✅ **User Registration** (`POST /auth/signup`)
- ✅ **User Login** (`POST /auth/login`)
- ✅ **Get Current User** (`GET /auth/me`)
- ✅ **JWT Token Authentication**
- ✅ **Password Hashing** (bcrypt)
- ✅ **Email Validation**
- ✅ **MongoDB User Storage**

### Frontend (React)
- ✅ **Login Page** - Beautiful, responsive design
- ✅ **Signup Page** - With password validation
- ✅ **Dashboard** - Protected area with user info
- ✅ **Auth Context** - State management for authentication
- ✅ **Auto-redirect** - Logged-in users go to dashboard
- ✅ **Logout Functionality**
- ✅ **Token Storage** - LocalStorage for persistence

---

## 🚀 How to Use

### 1. Access the Application

Open your browser and go to:
```
http://localhost:5175
```
(or whatever port your frontend is running on)

### 2. You'll See the Login Page

The login page will be displayed by default if you're not authenticated.

### 3. Create a New Account

Click **"Sign up"** button to go to the signup page.

**Fill in:**
- **Full Name**: Your name
- **Email**: Valid email address
- **Password**: Must meet these requirements:
  - At least 8 characters
  - At least 1 uppercase letter
  - At least 1 lowercase letter  
  - At least 1 digit
  - Example: `Password123`
- **Confirm Password**: Must match your password

Click **"Sign Up"** to create your account.

### 4. Login

After signup, you'll be automatically logged in. Or you can:
- Enter your **email**
- Enter your **password**
- Click **"Log In"**

### 5. Dashboard Access

Once logged in, you'll see:
- Welcome message with your name
- **Logout** button in the top-right
- Goal-Based Portfolio Planning form

### 6. Logout

Click the **"Logout"** button to sign out. You'll be redirected back to the login page.

---

## 📊 API Endpoints

### 1. Signup
```http
POST http://localhost:8000/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "StrongPass123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2025-11-13T10:30:00"
  }
}
```

### 2. Login
```http
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "StrongPass123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2025-11-13T10:30:00"
  }
}
```

### 3. Get Current User
```http
GET http://localhost:8000/auth/me?token=YOUR_JWT_TOKEN
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2025-11-13T10:30:00"
}
```

---

## 🔒 Security Features

### Password Requirements
- Minimum 8 characters
- Must contain uppercase letter
- Must contain lowercase letter
- Must contain at least one digit
- Passwords are hashed using **bcrypt** before storage

### JWT Tokens
- Tokens expire after **7 days**
- Stored securely in LocalStorage
- Used for API authentication
- HS256 algorithm

### Database
- Passwords are **never stored in plain text**
- Email uniqueness is enforced
- User accounts can be deactivated

---

## 🎨 UI Features

### Login Page
- **Modern gradient background** (purple/blue)
- **Smooth animations** (slide-up on load)
- **Error messages** with shake animation
- **Responsive design** for mobile devices
- **Quick switch** to signup page

### Signup Page
- **Password strength hints**
- **Real-time validation**
- **Confirm password** check
- **Detailed error messages**
- **Success auto-login**

### Dashboard
- **Welcome message** with user's name
- **Clean header** with gradient
- **Logout button** with hover effects
- **Portfolio planning** interface

---

## 📁 File Structure

```
backend/
├── app/
│   ├── routers/
│   │   └── auth.py              # Authentication endpoints
│   ├── schemas/
│   │   └── user.py              # User & Token models
│   ├── utils/
│   │   └── auth.py              # Password & JWT utilities
│   └── main.py                  # Auth router included

frontend/my-app/
├── src/
│   ├── context/
│   │   └── AuthContext.jsx      # Auth state management
│   ├── pages/
│   │   ├── Login.jsx            # Login page
│   │   ├── Signup.jsx           # Signup page
│   │   ├── Dashboard.jsx        # Protected dashboard
│   │   ├── Auth.css             # Auth pages styling
│   │   └── Dashboard.css        # Dashboard styling
│   └── App.jsx                  # Main app with auth logic
```

---

## 🧪 Testing the Authentication

### Test Signup
1. Go to http://localhost:5175
2. Click "Sign up"
3. Fill in the form:
   - Full Name: `Test User`
   - Email: `test@example.com`
   - Password: `TestPass123`
   - Confirm Password: `TestPass123`
4. Click "Sign Up"
5. You should be automatically logged in and see the dashboard

### Test Login
1. Logout using the button in the dashboard
2. On the login page, enter:
   - Email: `test@example.com`
   - Password: `TestPass123`
3. Click "Log In"
4. You should see the dashboard again

### Test API with curl
```bash
# Signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"api@test.com","password":"ApiTest123","full_name":"API User"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"api@test.com","password":"ApiTest123"}'
```

---

## 🔍 API Documentation

Visit the interactive API documentation:
```
http://localhost:8000/docs
```

You'll see:
- `/auth/signup` - User registration
- `/auth/login` - User authentication
- `/auth/me` - Get current user info

Try the endpoints directly from the Swagger UI!

---

## 🛠️ Troubleshooting

### Can't Login
- **Check password requirements** - Must have uppercase, lowercase, and digit
- **Verify email** - Must be a valid email format
- **Clear LocalStorage** - Open DevTools > Application > LocalStorage > Clear

### Token Expired
- Tokens last 7 days
- If expired, simply log in again
- Auto-logout will happen on failed auth

### Backend Errors
- **Check MongoDB** is running (local or Atlas)
- **Verify dependencies** are installed:
  ```bash
  pip install passlib[bcrypt] python-jose[cryptography] email-validator
  ```
- **Check backend logs** for detailed error messages

### CORS Issues
- Make sure backend `.env` has correct `CORS_ORIGINS`
- Should include your frontend URL (e.g., `http://localhost:5175`)

---

## 🎯 Next Steps

### Enhance Authentication
1. **Add "Remember Me"** checkbox
2. **Forgot Password** functionality
3. **Email verification**
4. **OAuth integration** (Google, GitHub)
5. **Two-factor authentication** (2FA)

### Add User Features
1. **Profile page** - Edit user information
2. **Change password** functionality
3. **User settings**
4. **Avatar upload**

### Protect API Routes
Add authentication requirement to other endpoints:
```python
from fastapi import Depends
from app.utils.auth import get_current_user

@router.post("/inputs")
async def create_input(
    data: InputData,
    current_user: UserResponse = Depends(get_current_user)
):
    # Only authenticated users can access
    ...
```

---

## 📞 Support

If you encounter any issues:
1. Check the browser console (F12)
2. Check backend terminal for errors
3. Verify MongoDB connection
4. Review API documentation at `/docs`

---

**Your authentication system is ready to use! 🎉**

Start by creating an account and exploring your portfolio management system!




