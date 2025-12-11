import logging
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from contextlib import asynccontextmanager

from app.operations import add, subtract, multiply, divide
from app.database import get_db, init_db, User, Calculation
from app.schemas import UserCreate, UserRead, UserLogin, CalculationCreate, CalculationRead
from app.calculation_factory import CalculationFactory
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


# ==================== CALCULATION ENDPOINTS (BREAD) ====================

@app.post("/calculations", response_model=CalculationRead, status_code=status.HTTP_201_CREATED)
def add_calculation(calc: CalculationCreate, user_id: int, db: Session = Depends(get_db)):
    """
    Create a new calculation record.
    Computes result using CalculationFactory and stores in database.
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
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
            user_id=user_id
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
def browse_calculations(user_id: int, db: Session = Depends(get_db)):
    """
    Browse all calculations for a user.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    calculations = db.query(Calculation).filter(Calculation.user_id == user_id).all()
    return [CalculationRead.model_validate(c) for c in calculations]


@app.get("/calculations/{calc_id}", response_model=CalculationRead)
def read_calculation(calc_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Read a specific calculation by ID.
    Verifies the calculation belongs to the user.
    """
    calc = db.query(Calculation).filter(
        (Calculation.id == calc_id) & (Calculation.user_id == user_id)
    ).first()
    
    if not calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    
    return CalculationRead.model_validate(calc)


@app.put("/calculations/{calc_id}", response_model=CalculationRead)
def edit_calculation(calc_id: int, calc_update: CalculationCreate, user_id: int, db: Session = Depends(get_db)):
    """
    Update an existing calculation.
    Recomputes result based on new operands/operation.
    """
    try:
        calc = db.query(Calculation).filter(
            (Calculation.id == calc_id) & (Calculation.user_id == user_id)
        ).first()
        
        if not calc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calculation not found"
            )
        
        # Compute new result
        result = CalculationFactory.compute(calc_update.operation, calc_update.operand_a, calc_update.operand_b)
        
        # Update fields
        calc.operation = calc_update.operation
        calc.operand_a = calc_update.operand_a
        calc.operand_b = calc_update.operand_b
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
def delete_calculation(calc_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Delete a calculation by ID.
    Verifies the calculation belongs to the user.
    """
    calc = db.query(Calculation).filter(
        (Calculation.id == calc_id) & (Calculation.user_id == user_id)
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

