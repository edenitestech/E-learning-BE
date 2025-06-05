================================ API DOCUMENTATION NAVIGATION PATTERNS ==================================

✅ ACCOUNT / AUTHENTICATION
POST   /api/auth/login/
POST   /api/auth/token/refresh/
POST   /api/auth/logout/
POST   /api/auth/register/
GET    /api/auth/profile/
PUT    /api/auth/profile/
GET    /api/auth/dashboard/
GET    /api/auth/gdpr/export/
DELETE /api/auth/gdpr/delete/

✅ COURSE CATEGORIES
GET    /api/categories/
POST   /api/categories/
GET    /api/categories/{id}/
PUT    /api/categories/{id}/
PATCH  /api/categories/{id}/
DELETE /api/categories/{id}/

✅ COURSES
GET    /api/courses/
POST   /api/courses/
GET    /api/courses/{course_id}/
PUT    /api/courses/{course_id}/
PATCH  /api/courses/{course_id}/
DELETE /api/courses/{course_id}/

▶ Nested Lessons
GET    /api/courses/{course_id}/lessons/
POST   /api/courses/{course_id}/lessons/
PUT    /api/courses/{course_id}/lessons/{lesson_id}/
PATCH  /api/courses/{course_id}/lessons/{lesson_id}/
DELETE /api/courses/{course_id}/lessons/{lesson_id}/

▶ Nested Quizzes
GET    /api/courses/{course_id}/quizzes/
POST   /api/courses/{course_id}/quizzes/
PUT    /api/courses/{course_id}/quizzes/{quiz_id}/
PATCH  /api/courses/{course_id}/quizzes/{quiz_id}/
DELETE /api/courses/{course_id}/quizzes/{quiz_id}/

▶ Final Exam Project
POST   /api/courses/{course_id}/exam-project/
POST   /api/courses/{course_id}/exam-project/{submission_id}/approve/

▶ Purchase Course (Paystack)
POST   /api/courses/{course_id}/purchase/

✅ PAYMENTS (Proxy for courses and exams)
POST   /api/payments/purchase/{course_id}/
POST   /api/payments/webhook/
GET    /api/payments/verify/{order_id}/

✅ LESSONS (flat, optional course filter)
GET    /api/lessons/?course={id}
POST   /api/lessons/
GET    /api/lessons/{lesson_id}/
PUT    /api/lessons/{lesson_id}/
PATCH  /api/lessons/{lesson_id}/
DELETE /api/lessons/{lesson_id}/

✅ FOLLOW-UP QUESTIONS (with nested options)
GET    /api/questions/?lesson={id}
POST   /api/questions/
GET    /api/questions/{question_id}/
PUT    /api/questions/{question_id}/
PATCH  /api/questions/{question_id}/
DELETE /api/questions/{question_id}/

POST   /api/questions/{question_id}/answer/
GET    /api/questions/{question_id}/explanation/

✅ ENROLLMENTS, PROGRESS, ANSWERS
GET    /api/enrollments/
POST   /api/enrollments/
GET    /api/enrollments/{enroll_id}/
PUT    /api/enrollments/{enroll_id}/
PATCH  /api/enrollments/{enroll_id}/
DELETE /api/enrollments/{enroll_id}/

GET    /api/progress/
POST   /api/progress/
GET    /api/progress/{progress_id}/
PUT    /api/progress/{progress_id}/
PATCH  /api/progress/{progress_id}/
DELETE /api/progress/{progress_id}/

GET    /api/answers/
POST   /api/answers/
GET    /api/answers/{answer_id}/
PUT    /api/answers/{answer_id}/
PATCH  /api/answers/{answer_id}/
DELETE /api/answers/{answer_id}/

✅ EXAMS / PAST QUESTIONS
GET    /api/exams/past-questions/
POST   /api/exams/past-questions/
GET    /api/exams/past-questions/{pq_id}/
PUT    /api/exams/past-questions/{pq_id}/
PATCH  /api/exams/past-questions/{pq_id}/
DELETE /api/exams/past-questions/{pq_id}/

▶ Past Question Practice Mode (one question)
POST   /api/exams/past-questions/practice/

▶ Past Question Quiz Mode (multiple answers)
POST   /api/exams/past-questions/quiz/

✅ SUBSCRIPTIONS FOR EXAMS (Paystack) — NEW
POST   /api/exams/subscribe/
GET    /api/exams/subscriptions/        ← List all your exam subscriptions
GET    /api/exams/subscriptions/verify/ ← Check active access by exam_type
