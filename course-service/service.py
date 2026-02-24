from data_service import CourseMockDataService

class CourseService:
    def __init__(self):
        self.data_service = CourseMockDataService()

    def get_all(self):
        return self.data_service.get_all()

    def get_by_id(self, course_id: int):
        return self.data_service.get_by_id(course_id)

    def create(self, course_data):
        return self.data_service.add(course_data)

    def update(self, course_id: int, course_data):
        return self.data_service.update(course_id, course_data)

    def delete(self, course_id: int):
        return self.data_service.delete(course_id)