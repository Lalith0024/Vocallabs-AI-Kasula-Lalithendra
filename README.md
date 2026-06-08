# Cold-Outreach Automation Pipeline

A production-grade, 4-stage automated email outreach pipeline built for SubSpace.

## Architecture
- **Backend**: FastAPI, Celery, SQLAlchemy, PostgreSQL, Redis
- **Frontend**: React, TypeScript, Vite, TailwindCSS
- **Orchestration**: Docker Compose

## API Integrations
The system connects to 4 APIs. If API keys are not provided in `.env`, the system gracefully falls back to mock data generators to ensure the pipeline runs end-to-end for demonstration purposes.
1. **Ocean.io**: Finds lookalike companies based on seed domain
2. **Prospeo**: Extracts decision-makers (C-suite, VPs)
3. **Eazyreach**: Resolves LinkedIn profiles to verified emails
4. **Brevo**: Sends personalized emails (requires manual approval at safety checkpoint)

## Setup & Running (Docker - Recommended)

1. **Prerequisites**: Docker & Docker Compose installed.
2. **Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys if you have them. Otherwise, leave blank for mock mode.
   ```
3. **Run**:
   ```bash
   docker-compose up -d --build
   ```

4. **Access**:
   - Frontend UI: http://localhost:3000 (or http://localhost:5173 depending on port binding)
   - Backend API Docs: http://localhost:8000/docs
   - Flower (Optional if added): http://localhost:5555

## Features
- **Zero manual handoffs**: Input a domain and the system pipelines data between APIs
- **Safety checkpoint**: Pauses before sending emails (Stage 4) for user approval via the UI
- **Real-time UI**: WebSockets broadcast pipeline status and metrics live to the dashboard
- **Graceful degradation**: Rate limits (Token Bucket), exponential backoff, and mock fallbacks built-in
- **Audit trail**: Every external API call is logged

## Structure
- `/backend`: FastAPI service + Celery workers
- `/frontend`: React SPA
