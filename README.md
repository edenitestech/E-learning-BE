================================ API NAVIGATION PATTERNS ==================================

=========Authentication=========
Register:  POST /api/auth/register/

Login:   POST /api/auth/login/

Token Refresh: POST /api/auth/token/refresh/

Profile:  GET/PUT /api/auth/profile/

Download my personal data: GET /api/auth/gdpr/export/

Delete my account: DELETE /api/auth/gdpr/delete/ 


========Courses App==============
Categories:  GET/POST /api/categories/

Single Category: GET/PUT/DELETE /api/categories/{id}/

Courses:  GET/POST /api/courses/

Single Course: GET/PUT/DELETE /api/courses/{id}/


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

