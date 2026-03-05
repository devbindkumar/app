# OpenRTB 2.5/2.6 Bidder with Campaign Manager - PRD

## Original Problem Statement
Build a Demand-Side Platform (DSP) Bidder that:
1. Receives and parses bid requests in OpenRTB 2.5 and 2.6 formats
2. Integrates with a Campaign Manager with comprehensive targeting
3. Makes real-time bidding decisions matching requests against campaigns
4. Constructs valid OpenRTB bid responses
5. Generates SSP endpoints with API key authentication

## User Personas
- **Ad Tech Professionals**: DSP operators managing programmatic campaigns
- **Campaign Managers**: Setting up targeting and budgets
- **SSP Integration Partners**: Sending bid requests via API

## Core Requirements (Static)
- OpenRTB 2.5 and 2.6 protocol support
- Dual-parse logic for version detection
- Campaign CRUD with comprehensive targeting
- Creative management (banner/video/native)
- SSP endpoint management with API keys
- Real-time bid logging and analytics
- Migration matrix documentation

## Architecture
- **Backend**: FastAPI + MongoDB
- **Frontend**: React + Tailwind + Shadcn
- **Bidding Engine**: Real-time matching with targeting rules
- **Protocol Handler**: Version detection, field migration

## What's Been Implemented

### Phase 1 - Core MVP (Completed)
- OpenRTB parser with 2.5/2.6 version detection
- Campaign Manager APIs (CRUD, activate/pause)
- Creative Management (banner/video/native)
- SSP Endpoint Management with API key auth
- Bid endpoint POST /api/bid with targeting engine
- Bid logging and statistics
- Dark theme dashboard with charts
- Campaigns, Creatives, SSP, Bid Logs pages

### Phase 2 - Advanced Bidding (Completed)
- Win/Billing notification callbacks
- Budget pacing (even distribution, hourly enforcement)
- Campaign performance reporting
- Bid shading (automatic price optimization)

### Phase 3 - Optimization Features (Completed)
- Frequency capping (in-memory via MongoDB)
- Supply Path Optimization (SPO)
- ML-based bid prediction (heuristic model)
- Custom report exports (CSV/JSON)
- API key auth removed from bid endpoint

### Phase 4 - Insights & Management (Completed - December 2025)
- **Campaign Performance Insights**
  - Health score analysis (0-100)
  - Issue detection (win rate, pacing, budget)
  - Actionable recommendations with one-click apply
  - Issues: Low win rate, underpacing, overspending
  - Actions: increase_bid, reduce_bid, enable_shading, enable_ml, enable_spo
  
- **ML Model Management Page**
  - View all ML-enabled campaigns
  - Training status and data points
  - Feature groups breakdown
  - Best/worst performing features
  - One-click model training
  
- **Multi-Currency Support**
  - Supported: USD, EUR, GBP, CAD, AUD, JPY
  - Currency selector in campaign form
  - Conversion API endpoint
  - Stored per campaign

## Key API Endpoints

### Bidding
- `POST /api/bid` - Main bid endpoint (no auth required)

### Campaigns
- `GET/POST /api/campaigns` - List/create campaigns
- `GET/PUT/DELETE /api/campaigns/{id}` - Single campaign ops
- `POST /api/campaigns/{id}/activate|pause` - Status changes

### Insights
- `GET /api/insights/campaigns` - All campaign insights
- `GET /api/insights/campaign/{id}` - Single campaign insight
- `POST /api/insights/apply-recommendation/{id}` - Apply fix

### ML Models
- `GET /api/ml/models` - List ML-enabled campaigns
- `GET /api/ml/model/{id}/details` - Model details
- `POST /api/ml/train/{id}` - Train model

### Currency
- `GET /api/currencies` - Supported currencies
- `GET /api/currency/convert` - Convert amount

### Reporting
- `GET /api/reports/summary` - Overall stats
- `GET /api/reports/export/csv` - CSV export
- `GET /api/reports/export/json` - JSON export

## Prioritized Backlog

### P0 - Completed
- [x] Core bidding engine
- [x] Campaign targeting
- [x] Win notifications
- [x] Budget pacing
- [x] Bid shading
- [x] Frequency capping
- [x] SPO
- [x] ML prediction
- [x] Campaign insights
- [x] ML model management
- [x] Multi-currency

### P1 - Upcoming
- [ ] Real-time dashboard WebSocket updates
- [ ] Advanced fraud detection

### P2 - Future
- [ ] Viewability prediction
- [ ] A/B testing framework
- [ ] Custom audience segments
- [ ] Native/audio ad formats
- [ ] Advanced analytics drill-down

## Tech Stack
- **Backend**: FastAPI, Motor (async MongoDB), Pydantic
- **Frontend**: React, Tailwind CSS, Shadcn/UI, Recharts, Axios
- **Database**: MongoDB
- **Domain**: Ad-Tech, OpenRTB, Programmatic Advertising
