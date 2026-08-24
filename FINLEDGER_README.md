# Finvoro — Personal Finance Management System

> A full-stack personal finance management application built as a **solo fresher project** to learn and demonstrate practical Django backend development.

**Project type:** Full-stack web application  
**Level:** Intermediate / Fresher portfolio  
**Backend:** Python + Django + Django REST Framework  
**Database:** PostgreSQL  
**Frontend:** HTML + CSS + Vanilla JavaScript  
**Authentication:** JWT  
**Containerization:** None  
**Kubernetes:** None  
**Architecture:** Modular monolith  
**Deployment:** Standard Django deployment

---

# 1. Project Overview

Finvoro is a personal finance application that allows users to manage their money through:

- Multiple financial accounts.
- Income and expense transactions.
- Categories.
- Budgets.
- Monthly financial summaries.
- Spending analysis.
- Transaction search and filtering.
- Authentication and user-specific data protection.

The application is designed to be more than a basic CRUD project.

The backend should demonstrate:

- REST API design.
- Authentication and authorization.
- Relational database design.
- PostgreSQL queries and aggregations.
- Data validation.
- Business rules.
- Database constraints.
- Transactions.
- Query optimization.
- Testing.
- Basic security.
- Frontend/backend integration.

The project should remain small enough for one fresher to understand completely.

---

# 2. Main Goal

The goal is **not** to build a banking application.

The goal is to build a realistic personal finance application that teaches the backend concepts expected from a junior/fresher Django developer.

You should eventually be able to explain:

> How the frontend communicates with Django, how Django validates requests, how data is stored in PostgreSQL, how permissions protect user data, how financial totals are calculated, and how the application is tested and deployed.

---

# 3. Technology Stack

## Backend

- Python
- Django
- Django REST Framework

## Database

- PostgreSQL

## Authentication

- JWT

## Frontend

- HTML5
- CSS3
- Vanilla JavaScript
- Fetch API

## Testing

- pytest
- pytest-django

## API Documentation

- OpenAPI / Swagger

## Version Control

- Git
- GitHub

## Explicitly Not Used

- Docker
- Kubernetes
- React
- Node.js backend
- Microservices
- Kafka
- Elasticsearch

Do not add technologies merely to make the resume look bigger.

---

# 4. Main Features

## Authentication

- [ ] User registration
- [ ] Login
- [ ] JWT access token
- [ ] JWT refresh token
- [ ] Logout strategy
- [ ] Current-user endpoint

## Accounts

Users can create accounts such as:

- Bank Account
- Cash
- Wallet
- Credit Card

Each account should have:

- Name
- Account type
- Initial balance
- Current balance
- Created date

## Transactions

Users can record:

- Income
- Expense

Each transaction should include:

- Account
- Category
- Amount
- Transaction type
- Date
- Description
- Created timestamp

## Categories

Examples:

- Food
- Transport
- Rent
- Shopping
- Salary
- Education
- Entertainment
- Healthcare
- Other

Users should have sensible control over categories.

## Budgets

Users can create budgets such as:

```text
Food
Monthly budget: ₹8,000
Spent: ₹6,250
Remaining: ₹1,750
```

## Reports

The backend should provide:

- Monthly income
- Monthly expenses
- Net balance/change
- Category-wise spending
- Account-wise balance
- Recent transactions

## Search and Filtering

Examples:

```text
Transactions by month
Transactions by category
Transactions by account
Transactions by transaction type
Transactions by date range
```

---

# 5. Core Data Model

Start with these models.

```text
User
 │
 ├── Account
 │
 ├── Category
 │
 ├── Transaction
 │
 └── Budget
```

Relationship example:

```text
User
  │
  ├── Account
  │      └── Transactions
  │
  ├── Category
  │      └── Transactions
  │
  └── Budget
         └── Category
```

Do not create unnecessary models at the beginning.

---

# 6. User

Use a custom Django User model.

Suggested fields:

```text
id
email
password
first_name
last_name
is_active
date_joined
updated_at
```

Requirements:

- Email should be unique.
- Password must use Django's password hashing.
- Never store plain-text passwords.
- Use the custom User model from the beginning.

---

# 7. Account

Suggested fields:

```text
id
user
name
account_type
initial_balance
created_at
updated_at
```

Example account types:

```text
BANK
CASH
WALLET
CREDIT_CARD
```

Important rule:

A user must only be able to access their own accounts.

---

# 8. Category

Suggested fields:

```text
id
user
name
category_type
created_at
```

Category types:

```text
INCOME
EXPENSE
```

Example:

```text
Salary       → INCOME
Food         → EXPENSE
Transport    → EXPENSE
```

You may later support system/default categories.

---

# 9. Transaction

This is the most important model.

Suggested fields:

```text
id
user
account
category
amount
transaction_type
date
description
created_at
updated_at
```

Transaction types:

```text
INCOME
EXPENSE
```

Rules:

- Amount must be greater than zero.
- Account must belong to the authenticated user.
- Category must be appropriate for the transaction type.
- User cannot create a transaction inside another user's account.
- Date cannot contain invalid values.
- Financial calculations must use safe decimal types rather than floating-point money values.

For monetary values, use a suitable decimal database field.

---

# 10. Budget

Suggested fields:

```text
id
user
category
amount
month
year
created_at
updated_at
```

Example:

```text
Category: Food
Month: August
Year: 2026
Budget: ₹8,000
```

Rules:

- Budget must belong to the authenticated user.
- Budget amount must be positive.
- A user should not create duplicate budgets for the same category/month/year combination.

This is a good place to use a database uniqueness constraint.

---

# 11. Important Business Logic

This project must contain real business logic.

## Balance

Example:

```text
Initial balance = ₹20,000
Income          = ₹30,000
Expenses        = ₹12,000

Current balance = ₹38,000
```

Conceptually:

```text
current balance
=
initial balance
+ total income
- total expenses
```

Do not blindly store duplicate calculated values unless you have a strong reason.

Prefer calculating or updating balances consistently.

---

# 12. Budget Calculation

Example:

```text
Food budget = ₹8,000

Food expenses:
₹1,200
₹800
₹2,300
₹1,000

Spent = ₹5,300
Remaining = ₹2,700
```

API should be able to return:

```json
{
  "budget": 8000,
  "spent": 5300,
  "remaining": 2700,
  "percentage_used": 66.25
}
```

---

# 13. API Structure

Use versioned APIs:

```text
/api/v1/
```

## Authentication

```text
POST /api/v1/auth/register/
POST /api/v1/auth/login/
POST /api/v1/auth/refresh/
GET  /api/v1/auth/me/
```

## Accounts

```text
GET    /api/v1/accounts/
POST   /api/v1/accounts/
GET    /api/v1/accounts/{id}/
PATCH  /api/v1/accounts/{id}/
DELETE /api/v1/accounts/{id}/
```

## Categories

```text
GET    /api/v1/categories/
POST   /api/v1/categories/
PATCH  /api/v1/categories/{id}/
DELETE /api/v1/categories/{id}/
```

## Transactions

```text
GET    /api/v1/transactions/
POST   /api/v1/transactions/
GET    /api/v1/transactions/{id}/
PATCH  /api/v1/transactions/{id}/
DELETE /api/v1/transactions/{id}/
```

## Budgets

```text
GET    /api/v1/budgets/
POST   /api/v1/budgets/
GET    /api/v1/budgets/{id}/
PATCH  /api/v1/budgets/{id}/
DELETE /api/v1/budgets/{id}/
```

## Reports

```text
GET /api/v1/reports/summary/
GET /api/v1/reports/monthly/
GET /api/v1/reports/categories/
GET /api/v1/reports/accounts/
```

---

# 14. Query Parameters

Transactions should support:

```text
?page=1
&category=food
&account=2
&transaction_type=EXPENSE
&start_date=2026-08-01
&end_date=2026-08-31
&ordering=-date
```

Example:

```text
GET /api/v1/transactions/?transaction_type=EXPENSE&start_date=2026-08-01&end_date=2026-08-31
```

This is important because it teaches practical API filtering rather than only CRUD.

---

# 15. Pagination

Do not return every transaction at once.

Example response:

```json
{
  "count": 120,
  "next": "...",
  "previous": null,
  "results": []
}
```

Start with page-number pagination.

Learn cursor pagination later only if necessary.

---

# 16. Authentication and Authorization

Authentication:

> Who is the user?

Authorization:

> What is the user allowed to access?

Examples:

```text
User A
  └── Account A
       └── Transaction A

User B
  └── Account B
       └── Transaction B
```

User A must never be able to request User B's transactions simply by changing an ID in the URL.

Every private endpoint must verify ownership.

---

# 17. Frontend

Do not use React.

Use:

```text
HTML
CSS
JavaScript
```

The frontend will communicate with the Django REST API using `fetch()`.

Suggested pages:

```text
login.html
register.html
dashboard.html
transactions.html
accounts.html
budgets.html
```

## Dashboard

Show:

```text
Total Balance
Monthly Income
Monthly Expenses
Remaining Budget
Recent Transactions
```

Keep the frontend simple.

The project is primarily a **backend project**.

---

# 18. Frontend Rule

Do not put important business rules only in JavaScript.

For example, JavaScript may check:

```text
amount > 0
```

for user experience.

But Django must check it again.

The backend is the source of truth.

---

# 19. Recommended Folder Structure

A reasonable structure:

```text
finvoro/
│
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
├── manage.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   ├── accounts/
│   ├── transactions/
│   ├── budgets/
│   └── reports/
│
├── frontend/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── transactions.html
│   ├── accounts.html
│   └── budgets.html
│
├── static/
│   ├── css/
│   └── js/
│
└── tests/
```

You may adjust the structure based on how you learn Django.

---

# 20. PHASE 1 — Project Setup

## Goal

Create a working Django project connected to PostgreSQL.

### Tasks

- [ ] Create GitHub repository.
- [ ] Create Python virtual environment.
- [ ] Install Django.
- [ ] Install Django REST Framework.
- [ ] Install PostgreSQL driver.
- [ ] Create Django project.
- [ ] Create initial apps.
- [ ] Configure PostgreSQL.
- [ ] Configure environment variables.
- [ ] Create `.gitignore`.
- [ ] Run migrations.
- [ ] Create admin user.
- [ ] Confirm Django starts correctly.

### You should understand

- Django project vs app.
- `manage.py`.
- Settings.
- URL routing.
- Migrations.
- Virtual environments.
- PostgreSQL connection.

### Finish condition

You can explain how a Django request reaches a view and how Django talks to PostgreSQL.

---

# 21. PHASE 2 — Custom User + JWT

## Goal

Implement secure authentication.

### Tasks

- [ ] Create custom User model.
- [ ] Make email unique.
- [ ] Configure authentication.
- [ ] Add JWT.
- [ ] Register endpoint.
- [ ] Login endpoint.
- [ ] Refresh token.
- [ ] `/me/` endpoint.
- [ ] Test protected endpoint.

### Learn

- Authentication vs authorization.
- Access token.
- Refresh token.
- Password hashing.
- HTTP 401 vs 403.

### Finish condition

A user can register, log in and access only authenticated endpoints.

---

# 22. PHASE 3 — Accounts

## Goal

Allow users to manage money sources.

### Tasks

- [ ] Create Account model.
- [ ] Create serializer.
- [ ] Create API.
- [ ] Add validation.
- [ ] Add permissions.
- [ ] Add CRUD.
- [ ] Test ownership.

Example:

```text
Bank Account
Cash Wallet
Savings Account
```

### Finish condition

User A cannot access User B's account.

---

# 23. PHASE 4 — Categories

## Goal

Create structured transaction categorization.

### Tasks

- [ ] Category model.
- [ ] Income/expense type.
- [ ] Category API.
- [ ] Validation.
- [ ] Ownership.
- [ ] Default category strategy.

### Finish condition

Categories work correctly and can be used by transactions.

---

# 24. PHASE 5 — Transactions

## Goal

Build the core feature.

### Tasks

- [ ] Transaction model.
- [ ] Income/expense support.
- [ ] Create transaction.
- [ ] List transactions.
- [ ] Update transaction.
- [ ] Delete transaction.
- [ ] Validation.
- [ ] Filtering.
- [ ] Pagination.
- [ ] Ordering.
- [ ] Ownership.

### Important rules

- Amount > 0.
- Account must belong to current user.
- Category must belong to current user or be a valid default category.
- Transaction type must match category type.

### Finish condition

You can record and retrieve reliable financial transactions.

---

# 25. PHASE 6 — Budgets

## Goal

Introduce business logic beyond CRUD.

### Tasks

- [ ] Budget model.
- [ ] Create budget.
- [ ] Prevent duplicates.
- [ ] Calculate spending.
- [ ] Calculate remaining budget.
- [ ] Calculate percentage used.
- [ ] Filter by month/year.

### Finish condition

A user can create a monthly category budget and see accurate usage.

---

# 26. PHASE 7 — Reports and Aggregations

## Goal

Use PostgreSQL for meaningful data analysis.

Create:

### Monthly summary

```text
Income
Expenses
Net change
```

### Category summary

```text
Food       ₹8,500
Transport  ₹3,200
Shopping   ₹7,000
```

### Account summary

```text
Bank       ₹50,000
Cash        ₹5,000
Wallet      ₹2,000
```

### Tasks

- [ ] `Sum`
- [ ] `Count`
- [ ] Grouping
- [ ] Date filters
- [ ] Monthly reports
- [ ] Category reports
- [ ] Account reports

### Finish condition

You can explain how your Django ORM query produces the report and what SQL-style operation it represents.

---

# 27. PHASE 8 — Database Quality

## Goal

Learn why database design matters.

Implement where justified:

- [ ] Unique constraints.
- [ ] Check constraints.
- [ ] Useful indexes.
- [ ] Proper foreign keys.
- [ ] Decimal fields for money.

Study:

- [ ] `select_related()`
- [ ] `prefetch_related()`
- [ ] N+1 queries.
- [ ] Query counting.
- [ ] `EXPLAIN ANALYZE`.

### Practical exercise

Find one endpoint that makes unnecessary database queries.

Measure it.

Optimize it.

Measure it again.

### Finish condition

You can explain at least one performance improvement you made.

---

# 28. PHASE 9 — Transactions and Consistency

## Goal

Understand database consistency.

Use transactions where multiple related database operations must succeed together.

Example:

```text
Create transaction
+
Update related balance
```

If your implementation requires both to succeed together, use a database transaction.

Learn:

- Atomicity.
- Rollback.
- Race conditions.
- Locking basics.

Do not add transactions blindly.

### Finish condition

You can explain why a transaction is needed for a specific operation in your project.

---

# 29. PHASE 10 — Testing

## Goal

Prove that the important rules work.

Test:

### Authentication

- [ ] Registration.
- [ ] Duplicate email.
- [ ] Login.
- [ ] Invalid login.
- [ ] Protected endpoint.

### Accounts

- [ ] Create account.
- [ ] Ownership.
- [ ] Update account.
- [ ] Unauthorized access.

### Transactions

- [ ] Create income.
- [ ] Create expense.
- [ ] Invalid amount.
- [ ] Wrong account ownership.
- [ ] Filtering.
- [ ] Pagination.

### Budgets

- [ ] Create budget.
- [ ] Duplicate budget.
- [ ] Spending calculation.

### Reports

- [ ] Monthly totals.
- [ ] Category totals.

### Finish condition

Important business rules have automated tests.

---

# 30. PHASE 11 — Frontend Integration

## Goal

Connect your HTML/CSS/JS frontend to the API.

### Tasks

- [ ] Register page.
- [ ] Login page.
- [ ] Store authentication state safely for your chosen architecture.
- [ ] Dashboard.
- [ ] Account page.
- [ ] Transaction page.
- [ ] Budget page.
- [ ] Fetch API data.
- [ ] Submit forms.
- [ ] Show validation errors.
- [ ] Show loading state.
- [ ] Show empty states.

### Important

Do not spend weeks designing a beautiful UI.

The UI only needs to demonstrate that your backend works.

---

# 31. PHASE 12 — API Documentation

Document:

- [ ] Authentication endpoints.
- [ ] Account endpoints.
- [ ] Category endpoints.
- [ ] Transaction endpoints.
- [ ] Budget endpoints.
- [ ] Report endpoints.
- [ ] Request examples.
- [ ] Response examples.
- [ ] Error examples.

Use OpenAPI/Swagger.

---

# 32. PHASE 13 — Security Review

Before deployment, verify:

- [ ] DEBUG disabled.
- [ ] Secret key not committed.
- [ ] Database credentials not committed.
- [ ] User ownership enforced.
- [ ] Input validation.
- [ ] Password hashing.
- [ ] Secure file/config handling if files are later added.
- [ ] CORS configured correctly.
- [ ] CSRF understanding.
- [ ] Proper permissions.
- [ ] No sensitive information in responses.

Ask yourself:

> Can User A access User B's financial information by changing an ID?

If yes, the project is not ready.

---

# 33. PHASE 14 — Deployment

No Docker.

Deploy using a standard Django-compatible hosting approach.

You need to understand:

- Environment variables.
- Production settings.
- PostgreSQL production database.
- Migrations.
- Static files.
- HTTPS.
- Logging.

The exact hosting provider is less important than understanding what you deployed.

---

# 34. PHASE 15 — GitHub Polish

Your repository should contain:

```text
README.md
requirements.txt
.env.example
source code
tests
frontend
```

Good commit examples:

```text
feat: add custom user authentication
feat: implement account management
feat: add transaction filtering
feat: add monthly reports
test: add transaction ownership tests
fix: prevent duplicate monthly budgets
perf: optimize transaction report query
docs: add API setup instructions
```

Avoid commits such as:

```text
update
final
final2
test
changes
```

---

# 35. Final Feature Scope

The completed project should contain approximately:

```text
Authentication
Accounts
Categories
Transactions
Budgets
Reports
Frontend
Tests
API Documentation
Deployment
```

That is enough.

Do not add:

```text
Payment gateway
Bank API integrations
Investment portfolio
Stock trading
Crypto
AI advisor
Chatbot
Mobile app
Microservices
```

unless the basic project is already finished and you deliberately want a future version.

---

# 36. Interview Topics Covered

By finishing this project properly, you should be prepared to discuss:

## Django

- Django project/app structure.
- Models.
- Migrations.
- ORM.
- QuerySets.
- Serializers.
- Views/ViewSets.
- URLs/routers.
- Permissions.
- Authentication.
- Middleware basics.
- Custom User model.

## PostgreSQL

- Primary key.
- Foreign key.
- Unique constraints.
- Check constraints.
- Indexes.
- Aggregations.
- Grouping.
- Transactions.
- Query optimization.

## Backend

- REST.
- HTTP methods.
- Status codes.
- JWT.
- Authentication vs authorization.
- Pagination.
- Filtering.
- Validation.
- Transactions.
- N+1 query problems.

---

# 37. Project-Specific Interview Questions

You should be able to answer:

1. Why did you choose Django?
2. Why PostgreSQL instead of SQLite?
3. Why did you create a custom User model?
4. How do you prevent User A from reading User B's transactions?
5. Why should money use Decimal rather than float?
6. How do you calculate monthly expenses?
7. How do you prevent duplicate budgets?
8. Where did you use database constraints?
9. Where would indexes help?
10. How would you optimize a slow report?
11. What happens if two requests update related financial data at the same time?
12. Why use JWT?
13. What is the difference between 401 and 403?
14. Why use pagination?
15. How does your JavaScript communicate with Django?
16. What validation happens in the frontend?
17. What validation happens in the backend?
18. Why must the backend validate data even if JavaScript already validates it?
19. What are the biggest security risks in your application?
20. What would you improve if the application had 100,000 users?

---

# 38. Fresher Interview Preparation Rule

Do not memorize answers.

For every major feature, know:

```text
What did I build?
Why did I build it?
How does it work?
What could go wrong?
How did I test it?
How could it be improved?
```

If you can answer those questions confidently, the project becomes useful in an interview.

---

# 39. Development Rule

Use AI as a mentor, not as the person who builds the project.

When working on each phase:

1. Understand the concept.
2. Try the implementation yourself.
3. Ask for help when blocked.
4. Show your code.
5. Fix the issue.
6. Write a test.
7. Explain what you learned.
8. Move to the next phase.

Do not ask for the entire project at once.

---

# 40. Master Prompt for Using AI While Building

Use this prompt with your coding assistant:

```text
I am building Finvoro, a personal finance management application.

I am a fresher learning Django backend development.

Stack:
- Python
- Django
- Django REST Framework
- PostgreSQL
- JWT
- HTML
- CSS
- Vanilla JavaScript

Do not use:
- React
- Docker
- Kubernetes
- Microservices

I want to build the project myself.

Your job is to act as my Django mentor and reviewer.

For the phase I give you:
1. Explain the concept briefly.
2. Explain what I need to build.
3. Tell me which files should change.
4. Give me a small task to implement myself.
5. Do not generate the entire project.
6. Do not move to later phases.
7. Review my implementation when I send it.
8. Point out correctness, security, database and performance issues.
9. Give hints before giving complete solutions.
10. Give me interview questions related to what I implemented.

The goal is understanding, not code generation.

Current phase:
[PASTE PHASE HERE]
```

---

# 41. Debugging Prompt

When something breaks:

```text
I am working on Finvoro.

Current phase:
[PHASE]

What I want:
[EXPECTED BEHAVIOR]

What happens:
[ACTUAL BEHAVIOR]

Error:
[ERROR MESSAGE]

Relevant code:
[CODE]

What I already tried:
[ATTEMPTS]

Do not rewrite the entire project.

First:
1. Identify the likely cause.
2. Explain the concept.
3. Give me a hint.
4. If I still cannot solve it, provide the smallest correction.
5. Explain why the correction works.
```

---

# 42. Code Review Prompt

```text
Review my Finvoro code like a senior Django backend engineer.

Check:

1. Correctness
2. Security
3. Authorization
4. Database design
5. Query efficiency
6. Django conventions
7. DRF conventions
8. Validation
9. Error handling
10. Testability

Classify each issue as:

CRITICAL
IMPORTANT
IMPROVEMENT
OPTIONAL

Do not rewrite everything.

Explain each issue and tell me how I should fix it.
Then ask me 5 interview questions about this code.
```

---

# 43. Completion Checklist

## Backend

- [ ] Custom User.
- [ ] JWT authentication.
- [ ] Accounts.
- [ ] Categories.
- [ ] Transactions.
- [ ] Budgets.
- [ ] Reports.
- [ ] Filtering.
- [ ] Pagination.
- [ ] Ownership permissions.
- [ ] Validation.
- [ ] Database constraints.
- [ ] Indexes where justified.
- [ ] Transactions where necessary.

## Frontend

- [ ] Register.
- [ ] Login.
- [ ] Dashboard.
- [ ] Accounts.
- [ ] Transactions.
- [ ] Budgets.
- [ ] Basic responsive CSS.
- [ ] API integration.

## Quality

- [ ] Automated tests.
- [ ] Swagger/OpenAPI.
- [ ] Clean Git history.
- [ ] Professional README.
- [ ] No secrets in repository.
- [ ] Production configuration.
- [ ] Deployment completed.

---

# 44. Definition of Done

Finvoro is complete when a user can:

```text
Register
   ↓
Login
   ↓
Create account
   ↓
Create categories
   ↓
Record income/expenses
   ↓
Create monthly budgets
   ↓
View dashboard
   ↓
Filter transactions
   ↓
View monthly reports
```

And the backend correctly enforces:

```text
Authentication
Authorization
Validation
Database constraints
Financial calculations
```

You should also be able to explain the project in an interview without reading the code.

---

# 45. What This Project Is Supposed to Demonstrate

Finvoro is not meant to show that you know every tool in backend engineering.

It is meant to show that you can take a real problem and build a working backend with:

```text
Django
    ↓
REST API
    ↓
Authentication
    ↓
Authorization
    ↓
PostgreSQL
    ↓
Business Logic
    ↓
Queries/Aggregations
    ↓
Testing
    ↓
Frontend Integration
    ↓
Deployment
```

For a fresher, that is a strong and realistic project scope.

---

# 46. Final Rule

**Do not add complexity just to make the project look impressive.**

A smaller project that you built yourself and can explain deeply is more valuable than a huge project containing technologies you cannot explain.

Build Finvoro phase by phase.
