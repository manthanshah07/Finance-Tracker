# Personal Finance & Investment Tracker

A production-quality web application built using **Django**, **Django REST Framework (DRF)**, **SQLite/MySQL**, **Bootstrap 5**, and **Chart.js**. This project is designed for IT Engineering college submissions, demonstrating advanced concepts in Python Programming, Database Normalization, Django MVT Architecture, Secure Authentication, REST APIs, File Handling (CSV), and Data Visualization.

---

## 1. PROJECT ABSTRACT

Managing personal finances is a key element of modern economic life, but users face friction in aggregating daily expenses, monthly budgeting, long-term Mutual Fund SIPs, equity stock portfolios, and future savings targets. The **Personal Finance & Investment Tracker** addresses this by providing a unified web application. 

The application enables daily expense logging, automatically triggers budget alerts when thresholds are crossed, calculates Systematic Investment Plan (SIP) profit/loss values, estimates stock portfolios based on dynamic market inputs, and visualizes progress on savings goals (e.g., Laptop, Emergency Fund). Built using Django's Model-View-Template (MVT) architecture, the project includes secure authentication, file importing/exporting (CSV), high-fidelity PDF report generation, and fully authenticated REST APIs.

---

## 2. SYSTEM ARCHITECTURE & MVC/MVT PATTERN

The application follows Django's standard **Model-View-Template (MVT)** pattern, which is a variation of the classic Model-View-Controller (MVC) architecture:

```mermaid
graph TD
    User([Browser User]) <-->|HTTP Request / Response| URL[URL Router - urls.py]
    URL <-->|Dispatches to| View[Views - views.py]
    View <-->|Queries / Saves| Model[Models - models.py]
    Model <-->|Reads / Writes| DB[(Database SQLite / MySQL)]
    View <-->|Serializes Data| DRF[Django REST Framework Serializers]
    DRF <-->|JSON Payload| API([REST API Consumer])
    View <-->|Injects Context| Template[Templates - HTML / CSS / JS / Chart.js]
    Template <-->|Renders UI| User
```

- **Model**: Represents the database structures. We define schemas for `UserProfile`, `Expense`, `SIPInvestment`, `StockInvestment`, and `SavingsGoal`.
- **View**: Acts as the controller, handling request-response cycles, business logic, calculations, file handling (CSV import/export, PDF drawing), and data parsing.
- **Template**: The user interface rendered using HTML5, CSS3, Bootstrap 5, and JavaScript. Data visualization is executed on the client-side using Chart.js.

---

## 3. DATABASE DESIGN & SCHEMA

The database is normalized to **3rd Normal Form (3NF)**. All tables are user-scoped, carrying a foreign key pointing to Django's built-in `auth_user` table with cascading deletions.

### ER Diagram Relationship Structure
- Each `User` has **one** corresponding `UserProfile` (1:1 Relationship).
- Each `User` can create **zero or many** `Expense` records (1:N Relationship).
- Each `User` can create **zero or many** `SIPInvestment` records (1:N Relationship).
- Each `User` can create **zero or many** `StockInvestment` records (1:N Relationship).
- Each `User` can create **zero or many** `SavingsGoal` records (1:N Relationship).

### Database Tables Schema

#### 1. `accounts_userprofile` (1:1 with auth_user)
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigInt | Primary Key, Auto-increment | Row identifier |
| `user_id` | Int | Unique, ForeignKey(auth_user) | Link to User account |
| `currency` | VarChar(3) | Choices: USD, EUR, INR, GBP... | Preferred currency code |
| `profile_pic` | VarChar(100) | Nullable | Path to profile image upload |
| `monthly_budget_limit` | Decimal(10, 2) | Default: 0.00 | Budget warning threshold |

#### 2. `expenses_expense` (1:N with auth_user)
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigInt | Primary Key, Auto-increment | Row identifier |
| `user_id` | Int | ForeignKey(auth_user) | Owner of the expense |
| `name` | VarChar(100) | Not Null | Expense name (e.g. Groceries) |
| `category` | VarChar(20) | Choices: Food, Bills, etc. | Group category |
| `amount` | Decimal(10, 2) | Not Null | Cost value |
| `date` | Date | Not Null | Date of transaction |
| `notes` | Text | Nullable | Optional text details |

#### 3. `investments_sipinvestment` (1:N with auth_user)
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigInt | Primary Key, Auto-increment | Row identifier |
| `user_id` | Int | ForeignKey(auth_user) | Owner of the SIP |
| `fund_name` | VarChar(150) | Not Null | Mutual Fund Name |
| `monthly_amount` | Decimal(10, 2) | Not Null | Monthly savings outlay |
| `start_date` | Date | Not Null | Start Date |
| `invested_amount` | Decimal(12, 2) | Not Null | Total cumulative capital invested |
| `current_value` | Decimal(12, 2) | Not Null | Current market valuation |

#### 4. `investments_stockinvestment` (1:N with auth_user)
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigInt | Primary Key, Auto-increment | Row identifier |
| `user_id` | Int | ForeignKey(auth_user) | Owner of the equity asset |
| `stock_name` | VarChar(150) | Not Null | Stock Company Name |
| `symbol` | VarChar(10) | Not Null | Stock Ticker (e.g. AAPL) |
| `quantity` | Int (unsigned) | Not Null | Number of shares held |
| `buy_price` | Decimal(10, 2) | Not Null | Purchase price per share |
| `current_price` | Decimal(10, 2) | Not Null | Current market price per share |

#### 5. `goals_savingsgoal` (1:N with auth_user)
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | BigInt | Primary Key, Auto-increment | Row identifier |
| `user_id` | Int | ForeignKey(auth_user) | Owner of the target |
| `name` | VarChar(100) | Not Null | Goal target (e.g. New Laptop) |
| `target_amount` | Decimal(12, 2) | Not Null | Target saving sum |
| `current_savings` | Decimal(12, 2) | Default: 0.00 | Capital accumulated so far |
| `target_date` | Date | Not Null | Expected achievement date |

---

## 4. REST API DOCUMENTATION

The REST API module is implemented via **Django REST Framework (DRF)**. All endpoints reside under the `/api/` prefix and require session authentication. Users are restricted to querying and modifying only their own records.

### Endpoints List

- `GET /api/expenses/` - List all expenses of the authenticated user
- `POST /api/expenses/` - Create a new expense (automatically assigns `user`)
- `PUT /api/expenses/<id>/` - Update an expense
- `DELETE /api/expenses/<id>/` - Delete an expense
- `GET /api/sips/` - List all SIP investments
- `POST /api/sips/` - Create a SIP
- `PUT /api/sips/<id>/` - Update a SIP
- `DELETE /api/sips/<id>/` - Delete a SIP
- `GET /api/stocks/` - List all stock holdings
- `POST /api/stocks/` - Create a stock holding
- `PUT /api/stocks/<id>/` - Update a stock holding
- `DELETE /api/stocks/<id>/` - Delete a stock holding
- `GET /api/goals/` - List all savings goals
- `POST /api/goals/` - Create a savings goal
- `PUT /api/goals/<id>/` - Update a savings goal
- `DELETE /api/goals/<id>/` - Delete a savings goal

### Sample API Request & Response

#### Request: `POST /api/expenses/`
**Headers**:
- `Content-Type: application/json`
- `X-CSRFToken: <token>`

**Body**:
```json
{
  "name": "Supermarket Groceries",
  "category": "Food",
  "amount": "84.50",
  "date": "2026-06-11",
  "notes": "Weekly snacks and items"
}
```

#### Response: `201 Created`
**Body**:
```json
{
  "id": 12,
  "name": "Supermarket Groceries",
  "category": "Food",
  "amount": "84.50",
  "date": "2026-06-11",
  "notes": "Weekly snacks and items"
}
```

---

## 5. SYSTEM SECURITY IMPLEMENTATION

1. **Authentication Protection**: Views are protected using Django's `@login_required` decorators or class-based `LoginRequiredMixin`.
2. **Access Isolation**: Every database query is scoped to the request user (e.g. `Expense.objects.filter(user=request.user)`), preventing any authenticated user from tampering with or viewing another user's financial datasets.
3. **Cross-Site Request Forgery (CSRF)**: All POST requests, including templates and AJAX integrations, require a valid `{% csrf_token %}` verification.
4. **Password Security**: Managed by Django's robust authentication backend, which implements PBKDF2 with a SHA256 hash by default.
5. **Form Validation**: Clean validation methods handle anomalies (e.g. checking matching passwords during registration, verifying file formats for CSV uploads, preventing negative amounts).

---

## 6. INSTALLATION & SETUP GUIDE

Follow these steps to run the application locally.

### Prerequisites
- Python 3.8 or above installed on your system.
- Pip (Python Package Installer).

### Steps

1. **Clone/Open Workspace**:
   Navigate to the project root directory:
   ```bash
   cd "c:\Users\LENOVO\Documents\Finance Tracker"
   ```

2. **Initialize Virtual Environment**:
   ```bash
   python -m venv venv
   ```
   Activate it:
   - On Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - On Mac/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute Database Migrations**:
   Create initial migration scripts:
   ```bash
   python manage.py makemigrations
   ```
   Apply them to create database tables:
   ```bash
   python manage.py migrate
   ```

5. **Create an Admin Superuser**:
   ```bash
   python manage.py createsuperuser
   ```
   *(Follow the prompts to enter username, email, and password)*

6. **Start the Development Server**:
   ```bash
   python manage.py runserver
   ```
   Access the application in your browser at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 7. SYSTEM TESTS

To verify calculations, authentication gates, and API constraints, execute the test suite:
```bash
python manage.py test
```


## 7. CONCLUSION & FUTURE SCOPE

The Personal Finance & Investment Tracker successfully implements a secure, normalized, and visually compelling financial dashboard. 

### Future Enhancements:
- **Live Market API Integration**: Fetch real-time stock prices and mutual fund NAVs using APIs like AlphaVantage or Yahoo Finance.
- **AI-Driven Budgeting**: Implement machine learning models to classify expenses and predict cash flows or budget overflows.
- **Tax Optimization**: Add modules to calculate tax deductions based on tax regimes and mutual fund holdings (ELSS).
- **Automated Bank Alerts Integration**: Allow scanning email receipts or SMS notifications to auto-add expenses.
