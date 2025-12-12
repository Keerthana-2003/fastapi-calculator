import logging
from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.operations import add, subtract, multiply, divide
from app.database import get_db, init_db, User, Calculation
from app.schemas import (
    UserCreate,
    UserRead,
    UserLogin,
    UserUpdate,
    PasswordChange,
    CalculationCreate,
    CalculationRead,
    AuthResponse,
    CalculationUpdate,
)
from app.calculation_factory import CalculationFactory
from app.security import hash_password, verify_password, create_access_token, decode_access_token

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

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

bearer_scheme = HTTPBearer(auto_error=False)


# Root endpoint
@app.get("/")
def root():
    return {"message": "FastAPI Calculator is running! Visit /docs for API documentation."}


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    """Resolve current user from JWT if provided; return None when absent."""
    if not credentials:
        return None
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            raise ValueError("Missing user id in token")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the current authenticated user or raise when missing/invalid."""
    user = get_current_user_optional(credentials, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized")
    return user


def _build_auth_response(db_user: User) -> AuthResponse:
    """Create a JWT and wrap the user response."""
    token = create_access_token({"sub": db_user.email, "user_id": db_user.id}, expires_delta=timedelta(hours=1))
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserRead.model_validate(db_user),
    )


def _create_user_record(user: UserCreate, db: Session) -> User:
    """Create a user record with hashed password, raising HTTPException on conflicts."""
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    try:
        hashed_password = hash_password(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            password_hash=hashed_password,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logging.info(f"User registered successfully: {user.username}")
        return db_user
    except IntegrityError as e:
        db.rollback()
        logging.error(f"Database integrity error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )
    except Exception as e:  # pragma: no cover - unexpected
        db.rollback()
        logging.error(f"Error registering user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user",
        )


def _authenticate_user(credentials: UserLogin, db: Session) -> User:
    db_user = db.query(User).filter(User.email == credentials.email).first()
    if not db_user or not verify_password(credentials.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return db_user


# ==================== USER ENDPOINTS ====================

@app.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user and return a JWT."""
    db_user = _create_user_record(user, db)
    return _build_auth_response(db_user)


@app.post("/users/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Backward-compatible registration route returning user info only."""
    db_user = _create_user_record(user, db)
    return UserRead.model_validate(db_user)


@app.post("/login", response_model=AuthResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate and return JWT + user payload."""
    db_user = _authenticate_user(credentials, db)
    logging.info(f"User logged in successfully: {db_user.username}")
    return _build_auth_response(db_user)


@app.post("/users/login")
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """Backward-compatible login returning message + user."""
    db_user = _authenticate_user(credentials, db)
    logging.info(f"User logged in successfully: {db_user.username}")
    return {
        "message": "Login successful",
        "user": UserRead.model_validate(db_user),
    }


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


@app.get("/register.html", include_in_schema=False)
def serve_register_page():
    return FileResponse(STATIC_DIR / "register.html")


@app.get("/login.html", include_in_schema=False)
def serve_login_page():
    return FileResponse(STATIC_DIR / "login.html")


@app.get("/calculations.html", include_in_schema=False)
def serve_calculations_page():
    return FileResponse(STATIC_DIR / "calculations.html")


@app.get("/profile.html", include_in_schema=False)
def serve_profile_page():
    return FileResponse(STATIC_DIR / "profile.html")


@app.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user."""
    return UserRead.model_validate(current_user)


@app.put("/me", response_model=AuthResponse)
def update_current_user(
    update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update username/email for the current user and return a fresh JWT."""
    if update.username is None and update.email is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided")

    try:
        if update.username and update.username != current_user.username:
            existing_username = db.query(User).filter(
                (User.username == update.username) & (User.id != current_user.id)
            ).first()
            if existing_username:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
            current_user.username = update.username

        if update.email and update.email != current_user.email:
            existing_email = db.query(User).filter(
                (User.email == update.email) & (User.id != current_user.id)
            ).first()
            if existing_email:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken")
            current_user.email = update.email

        db.commit()
        db.refresh(current_user)
        return _build_auth_response(current_user)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        db.rollback()
        logging.error(f"Error updating profile: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating profile")


@app.post("/me/password", response_model=AuthResponse)
def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change the current user's password and return a fresh JWT."""
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")

    current_user.password_hash = hash_password(payload.new_password)
    db.commit()
    db.refresh(current_user)
    logging.info(f"Password updated for user {current_user.id}")
    return _build_auth_response(current_user)


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


# ==================== CALCULATION ENDPOINTS (BREAD) ====================

@app.post("/calculations", response_model=CalculationRead, status_code=status.HTTP_201_CREATED)
def add_calculation(
    calc: CalculationCreate,
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Create a new calculation record.
    Computes result using CalculationFactory and stores in database.
    """
    try:
        target_user_id = user_id or (current_user.id if current_user else None)
        if not target_user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized")

        # Verify user exists (for backward compatibility when user_id is passed)
        user = db.query(User).filter(User.id == target_user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Compute result using factory
        result = CalculationFactory.compute(calc.operation, calc.operand_a, calc.operand_b)
        
        # Create calculation record
        db_calc = Calculation(
            operation=calc.operation,
            operand_a=calc.operand_a,
            operand_b=calc.operand_b,
            result=result,
            user_id=target_user_id,
        )
        
        db.add(db_calc)
        db.commit()
        db.refresh(db_calc)
        
        logging.info(f"Calculation created: {calc.operation}({calc.operand_a}, {calc.operand_b}) = {result}")
        return CalculationRead.model_validate(db_calc)
        
    except HTTPException:
        raise
    except ValueError as e:
        logging.error(f"Invalid calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating calculation"
        )


@app.get("/calculations", response_model=list[CalculationRead])
def browse_calculations(
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Browse all calculations for a user.
    """
    target_user_id = user_id or (current_user.id if current_user else None)
    if not target_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized")

    user = db.query(User).filter(User.id == target_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    calculations = db.query(Calculation).filter(Calculation.user_id == target_user_id).all()
    return [CalculationRead.model_validate(c) for c in calculations]


@app.get("/calculations/{calc_id}", response_model=CalculationRead)
def read_calculation(
    calc_id: int,
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Read a specific calculation by ID.
    Verifies the calculation belongs to the user.
    """
    target_user_id = user_id or (current_user.id if current_user else None)
    if not target_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized")

    calc = db.query(Calculation).filter(
        (Calculation.id == calc_id) & (Calculation.user_id == target_user_id)
    ).first()
    
    if not calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    
    return CalculationRead.model_validate(calc)


@app.put("/calculations/{calc_id}", response_model=CalculationRead)
def edit_calculation(
    calc_id: int,
    calc_update: CalculationUpdate,
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Update an existing calculation.
    Recomputes result based on new operands/operation.
    """
    try:
        target_user_id = user_id or (current_user.id if current_user else None)
        if not target_user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized")

        calc = db.query(Calculation).filter(
            (Calculation.id == calc_id) & (Calculation.user_id == target_user_id)
        ).first()
        
        if not calc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calculation not found"
            )
        
        # Use existing values when fields are omitted
        new_operation = calc_update.operation or calc.operation
        new_a = calc_update.operand_a if calc_update.operand_a is not None else calc.operand_a
        new_b = calc_update.operand_b if calc_update.operand_b is not None else calc.operand_b

        # Compute new result
        result = CalculationFactory.compute(new_operation, new_a, new_b)
        
        # Update fields
        calc.operation = new_operation
        calc.operand_a = new_a
        calc.operand_b = new_b
        calc.result = result
        
        db.commit()
        db.refresh(calc)
        
        logging.info(f"Calculation {calc_id} updated")
        return CalculationRead.model_validate(calc)
        
    except HTTPException:
        raise
    except ValueError as e:
        logging.error(f"Invalid calculation update: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        logging.error(f"Error updating calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating calculation"
        )


@app.delete("/calculations/{calc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(
    calc_id: int,
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Delete a calculation by ID.
    Verifies the calculation belongs to the user.
    """
    target_user_id = user_id or (current_user.id if current_user else None)
    if not target_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized")

    calc = db.query(Calculation).filter(
        (Calculation.id == calc_id) & (Calculation.user_id == target_user_id)
    ).first()
    
    if not calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    
    db.delete(calc)
    db.commit()
    
    logging.info(f"Calculation {calc_id} deleted")
    return None

