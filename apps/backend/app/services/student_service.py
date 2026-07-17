import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User
from app.repositories.student_repository import StudentRepository
from app.repositories.user_repository import UserRepository
from app.schemas.student import StudentCreateRequest, StudentSelfUpdateRequest, StudentUpdateRequest
from app.services.auth_service import AuthService, EmailAlreadyExistsError


class StudentNotFoundError(Exception):
    pass


class DuplicateStudentError(Exception):
    pass


class StudentService:
    """Business logic for student profile management.

    Composes AuthService (Authentication Module, unmodified) for account
    creation and StudentRepository for profile persistence.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = StudentRepository(db)
        self.user_repo = UserRepository(db)
        self.auth_service = AuthService(db)

    def create_student(self, payload: StudentCreateRequest):
        if self.repo.get_by_student_id(payload.student_id) is not None:
            raise DuplicateStudentError("student_id already exists")

        try:
            user = self.auth_service.create_student(
                full_name=payload.full_name, email=payload.email, password=payload.password
            )
        except EmailAlreadyExistsError:
            raise DuplicateStudentError("email already registered")

        try:
            profile = self.repo.create_profile(
                user_id=user.id,
                student_id=payload.student_id,
                college_name=payload.college_name,
                department=payload.department,
                semester=payload.semester,
                graduation_year=payload.graduation_year,
                phone_number=payload.phone_number,
                skills=payload.skills,
                resume_url=payload.resume_url,
            )
            self.repo.commit()
        except IntegrityError:
            # AuthService.create_student already committed the User row
            # independently (Authentication Module is not modified here), so
            # true cross-table atomicity isn't available. Compensate by
            # deactivating the orphaned account rather than leaving a broken
            # profile-less user silently active.
            self.db.rollback()
            self.user_repo.set_refresh_token_hash(user, None)
            user.is_active = False
            self.user_repo.commit()
            raise DuplicateStudentError("student_id already exists")

        self.repo.refresh(profile)
        return profile, user

    def list_students(self, *, search: str | None, page: int, page_size: int):
        return self.repo.list_students(search=search, page=page, page_size=page_size)

    def get_student(self, profile_id: uuid.UUID):
        profile = self.repo.get_by_id(profile_id)
        if profile is None:
            raise StudentNotFoundError()
        return profile, profile.user

    def update_student(self, profile_id: uuid.UUID, payload: StudentUpdateRequest):
        profile = self.repo.get_by_id(profile_id)
        if profile is None:
            raise StudentNotFoundError()

        if payload.student_id and payload.student_id != profile.student_id:
            existing = self.repo.get_by_student_id(payload.student_id)
            if existing is not None:
                raise DuplicateStudentError("student_id already exists")
            profile.student_id = payload.student_id

        for field in (
            "college_name",
            "department",
            "semester",
            "graduation_year",
            "phone_number",
            "skills",
            "resume_url",
        ):
            value = getattr(payload, field)
            if value is not None:
                setattr(profile, field, value)

        if payload.full_name is not None:
            profile.user.full_name = payload.full_name
        if payload.is_active is not None:
            profile.user.is_active = payload.is_active

        self.repo.commit()
        self.repo.refresh(profile)
        return profile, profile.user

    def delete_student(self, profile_id: uuid.UUID) -> None:
        profile = self.repo.get_by_id(profile_id)
        if profile is None:
            raise StudentNotFoundError()
        self.repo.delete(profile)
        self.repo.commit()

    def get_own_profile(self, user: User):
        profile = self.repo.get_by_user_id(user.id)
        if profile is None:
            raise StudentNotFoundError()
        return profile, user

    def update_own_profile(self, user: User, payload: StudentSelfUpdateRequest):
        profile = self.repo.get_by_user_id(user.id)
        if profile is None:
            raise StudentNotFoundError()

        for field in (
            "college_name",
            "department",
            "semester",
            "graduation_year",
            "phone_number",
            "skills",
            "resume_url",
        ):
            value = getattr(payload, field)
            if value is not None:
                setattr(profile, field, value)

        self.repo.commit()
        self.repo.refresh(profile)
        return profile, user

    def get_dashboard(self, user: User):
        profile = self.repo.get_by_user_id(user.id)
        if profile is None:
            raise StudentNotFoundError()

        total_problems = self.repo.count_active_hackathon_problems()
        submissions_count = self.repo.count_submissions_for_user(user.id)
        best_score = self.repo.best_score_for_user(user.id)

        return profile, user, total_problems, submissions_count, best_score
