# BillFlow - Professional Billing Software

A modern, web-based billing and invoicing SaaS for small businesses and freelancers.

![BillFlow](https://img.shields.io/badge/Version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![React](https://img.shields.io/badge/React-18.2-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- ✅ **Invoice Management** - Create, edit, send, and track invoices
- ✅ **PDF Generation** - Professional PDF invoices with your branding
- ✅ **Email Invoices** - Send invoices directly to clients
- ✅ **Client Management** - Manage your client database
- ✅ **Product Catalog** - Reusable products and services
- ✅ **Tax Handling** - Multiple tax rates support
- ✅ **Dashboard & Reports** - Revenue insights and analytics
- ✅ **Multi-user Support** - Owner and member roles

## Tech Stack

### Backend
- **FastAPI** (Python) - Modern async API framework
- **Supabase** - PostgreSQL database, Auth, and Storage
- **Pydantic** - Data validation
- **ReportLab** - PDF generation
- **Resend** - Email delivery

### Frontend
- **React 18** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Zustand** - State management
- **React Hook Form** - Form handling
- **Recharts** - Charts

## Project Structure

```
billing-software/
├── backend/
│   ├── app/
│   │   ├── api/v1/           # API endpoints
│   │   ├── core/             # Config, security, dependencies
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── repositories/     # Database operations
│   │   ├── services/         # Business logic
│   │   └── main.py           # FastAPI app
│   ├── supabase/migrations/  # Database migrations
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── layouts/          # Page layouts
│   │   ├── pages/            # Page components
│   │   ├── stores/           # Zustand stores
│   │   └── lib/              # API client, utilities
│   └── package.json
│
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase account

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

5. Configure environment variables in `.env`:
   ```
   SUPABASE_URL=your-supabase-url
   SUPABASE_KEY=your-anon-key
   SUPABASE_SERVICE_KEY=your-service-key
   JWT_SECRET=your-jwt-secret
   RESEND_API_KEY=your-resend-key
   ```

6. Run the database migration in Supabase:
   - Go to Supabase Dashboard > SQL Editor
   - Run the SQL from `supabase/migrations/001_initial_schema.sql`

7. Start the backend:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

4. Open http://localhost:3000

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Environment Variables

### Backend (.env)

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase anon/public key |
| `SUPABASE_SERVICE_KEY` | Supabase service role key |
| `JWT_SECRET` | JWT signing secret (from Supabase) |
| `JWT_ALGORITHM` | JWT algorithm (default: HS256) |
| `RESEND_API_KEY` | Resend API key for emails |
| `FROM_EMAIL` | Sender email address |

## Architecture

The application follows a clean architecture pattern:

```
API Layer → Service Layer → Repository Layer → Database
```

- **API Layer**: HTTP request/response handling
- **Service Layer**: Business logic and validations
- **Repository Layer**: Database operations
- **Models/Schemas**: Data structures

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

---

Built with ❤️ for small businesses and freelancers.

