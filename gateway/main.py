# gateway/main.py

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
import httpx
import time
from typing import Any

app = FastAPI(title="API Gateway", version="1.0.0")

# ==============================
# JWT CONFIGURATION (Activity 2)
# ==============================

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ==============================
# LOGGING MIDDLEWARE (Activity 3)
# ==============================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    print(f"Incoming Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    print(f"Completed in {process_time:.4f}s | Status: {response.status_code}")
    
    return response

# ==============================
# GLOBAL ERROR HANDLER (Activity 4)
# ==============================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "message": "This error was handled by the API Gateway"
        }
    )

# ==============================
# LOGIN ENDPOINT (With Username & Password)
# ==============================

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    if form_data.username != "admin" or form_data.password != "1234":
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token({"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ==============================
# SERVICES & ROUTING (Activity 1)
# ==============================

SERVICES = {
    "student": "http://localhost:8001",
    "course": "http://localhost:8002"
}

async def forward_request(service: str, path: str, method: str, **kwargs) -> Any:
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")

    url = f"{SERVICES[service]}{path}"

    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, **kwargs)
            elif method == "POST":
                response = await client.post(url, **kwargs)
            elif method == "PUT":
                response = await client.put(url, **kwargs)
            elif method == "DELETE":
                response = await client.delete(url, **kwargs)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")

            # Handle Microservice level errors gracefully
            if response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            return JSONResponse(
                content=response.json() if response.text else None,
                status_code=response.status_code
            )

        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

# ==============================
# ROOT
# ==============================

@app.get("/")
def read_root():
    return {"message": "API Gateway is running", "available_services": list(SERVICES.keys())}

# ==============================
# STUDENT ROUTES (PROTECTED)
# ==============================

@app.get("/gateway/students", dependencies=[Depends(verify_token)])
async def get_all_students():
    return await forward_request("student", "/api/students", "GET")

@app.get("/gateway/students/{student_id}", dependencies=[Depends(verify_token)])
async def get_student(student_id: int):
    return await forward_request("student", f"/api/students/{student_id}", "GET")

@app.post("/gateway/students", dependencies=[Depends(verify_token)])
async def create_student(request: Request):
    body = await request.json()
    return await forward_request("student", "/api/students", "POST", json=body)

@app.put("/gateway/students/{student_id}", dependencies=[Depends(verify_token)])
async def update_student(student_id: int, request: Request):
    body = await request.json()
    return await forward_request("student", f"/api/students/{student_id}", "PUT", json=body)

@app.delete("/gateway/students/{student_id}", dependencies=[Depends(verify_token)])
async def delete_student(student_id: int):
    return await forward_request("student", f"/api/students/{student_id}", "DELETE")

# ==============================
# COURSE ROUTES (PROTECTED) - Activity 1
# ==============================

@app.get("/gateway/courses", dependencies=[Depends(verify_token)])
async def get_courses():
    return await forward_request("course", "/api/courses", "GET")

@app.get("/gateway/courses/{course_id}", dependencies=[Depends(verify_token)])
async def get_course(course_id: int):
    return await forward_request("course", f"/api/courses/{course_id}", "GET")

@app.post("/gateway/courses", dependencies=[Depends(verify_token)])
async def create_course(request: Request):
    body = await request.json()
    return await forward_request("course", "/api/courses", "POST", json=body)

@app.put("/gateway/courses/{course_id}", dependencies=[Depends(verify_token)])
async def update_course(course_id: int, request: Request):
    body = await request.json()
    return await forward_request("course", f"/api/courses/{course_id}", "PUT", json=body)

@app.delete("/gateway/courses/{course_id}", dependencies=[Depends(verify_token)])
async def delete_course(course_id: int):
    return await forward_request("course", f"/api/courses/{course_id}", "DELETE")