import logging
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from contextlib import asynccontextmanager

from app.operations import add, subtract, multiply, divide
from app.database import get_db, init_db, User
from app.schemas import UserCreate, UserRead, UserLogin
from app.security import hash_password, verify_password

# Set up logging
logging.basicConfig(level=logging.INFO)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    try:
        init_db()
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
    yield


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="FastAPI Calculator",
    description="A simple calculator API",
    lifespan=lifespan
)


# Root endpoint
@app.get("/")
def root():
    return {"message": "FastAPI Calculator is running! Visit /docs for API documentation."}


# ==================== USER ENDPOINTS ====================

@app.post("/users/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with unique username and email.
    Password is hashed before storing in database.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    try:
        # Hash the password
        hashed_password = hash_password(user.password)
        
        # Create new user
        db_user = User(
            username=user.username,
            email=user.email,
            password_hash=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logging.info(f"User registered successfully: {user.username}")
        # Return a Pydantic model validated from the SQLAlchemy object
        return UserRead.model_validate(db_user)
        
    except IntegrityError as e:
        db.rollback()
        logging.error(f"Database integrity error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    except Exception as e:
        db.rollback()
        logging.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )


@app.post("/users/login")
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login user with email and password.
    Verifies password hash against stored hash.
    """
    try:
        # Find user by email
        db_user = db.query(User).filter(User.email == credentials.email).first()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, db_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        logging.info(f"User logged in successfully: {db_user.username}")
        # Use Pydantic v2 model validation for SQLAlchemy object
        return {
            "message": "Login successful",
            "user": UserRead.model_validate(db_user)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login"
        )


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user details by ID"""
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Return as Pydantic model for consistent serialization
    return UserRead.model_validate(db_user)


# ==================== CALCULATOR ENDPOINTS ====================

# Add endpoint
@app.get("/add")
def api_add(a: float, b: float):
    result = add(a, b)
    logging.info(f"Adding {a} + {b} = {result}")
    return {"result": result}


# Subtract endpoint
@app.get("/subtract")
def api_subtract(a: float, b: float):
    result = subtract(a, b)
    logging.info(f"Subtracting {a} - {b} = {result}")
    return {"result": result}


# Multiply endpoint
@app.get("/multiply")
def api_multiply(a: float, b: float):
    result = multiply(a, b)
    logging.info(f"Multiplying {a} * {b} = {result}")
    return {"result": result}


# Divide endpoint
@app.get("/divide")
def api_divide(a: float, b: float):
    try:
        result = divide(a, b)
        logging.info(f"Dividing {a} / {b} = {result}")
        return {"result": result}
    except ValueError as e:
        logging.error(f"Error dividing {a} / {b}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
