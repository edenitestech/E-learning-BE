================================ API DOCUMENTATION NAVIGATION PATTERNS ==================================

=========Authentication=========
Register:  POST /api/auth/register/

Login:   POST /api/auth/login/

Logout: POST /api/auth/logout/

Token Refresh: POST /api/auth/token/refresh/

Profile:  GET/PUT /api/auth/profile/

Dashboard: GET /api/auth/dashboard/

Download my personal data: GET /api/auth/gdpr/export/

Delete my account: DELETE /api/auth/gdpr/delete/ 


========Courses App==============
Categories:  GET/POST /api/categories/

Single Category: GET/PUT/DELETE /api/categories/{id}/

Courses:  GET/POST /api/courses/

Single Course: GET/PUT/DELETE /api/courses/{id}/

Purchase course: POST /api/courses/{id}/purchase/


==========Content App==============
Lessons:  GET/POST /api/lessons/

Single Lesson: GET/PUT/DELETE /api/lessons/{id}/

Questions:  GET/POST /api/questions/

Single Question: GET/PUT/DELETE /api/questions/{id}/

Submit Answer: POST /api/questions/{id}/answer/

Get Explanation: GET /api/questions/{id}/explanation/


===========Enrollments App==============
Enrollments: GET/POST /api/enrollments/

Single Enrollment: GET/PUT/DELETE /api/enrollments/{id}/

Progress:  GET/POST /api/progress/

Single Progress: GET/PUT/DELETE /api/progress/{id}/

Answers:  GET/POST /api/answers/

Single Answer: GET/PUT/DELETE /api/answers/{id}/

Payment webhook: POST /api/payments/webhook/


===========Exams App==============
JAMB/WAEC past questions: GET /api/exams/past-questions/?exam_type=JAMB&year=2023

===========jamb and testimonials Apps=======================
GET /api/jamb/subjects/

GET /api/jamb/subjects/<slug>/questions/

GET /api/jamb/strategies/

GET /api/testimonials/