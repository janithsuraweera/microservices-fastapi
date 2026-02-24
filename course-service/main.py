from fastapi import FastAPI, HTTPException, status
from typing import List
from models import Course, CourseCreate, CourseUpdate
from service import CourseService

app = FastAPI(title="Course Microservice")

course_service = CourseService()

@app.get("/api/courses", response_model=List[Course])
def get_courses():
    return course_service.get_all()

@app.get("/api/courses/{course_id}", response_model=Course)
def get_course(course_id: int):
    course = course_service.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.post("/api/courses", response_model=Course, status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate):
    return course_service.create(course)

@app.put("/api/courses/{course_id}", response_model=Course)
def update_course(course_id: int, course: CourseUpdate):
    updated = course_service.update(course_id, course)
    if not updated:
        raise HTTPException(status_code=404, detail="Course not found")
    return updated

@app.delete("/api/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int):
    success = course_service.delete(course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")