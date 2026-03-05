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

### Phase 1 (Completed)
- Backend Core:
  - OpenRTB parser with 2.5/2.6 version detection
  - Campaign Manager APIs (CRUD, activate/pause)
  - Creative Management (banner/video/native)
  - SSP Endpoint Management with API key auth
  - Bid endpoint POST /api/bid with targeting engine
  - Bid logging and statistics
  - Migration matrix endpoint

- Frontend Core:
  - Dark theme dashboard with charts (Recharts)
  - Campaigns list with status management
  - Campaign form with multi-tab targeting configuration
  - Creatives grid with type badges
  - SSP Endpoints with API key reveal/copy
  - Bid Logs with real-time monitoring
  - Migration Matrix reference page

### Phase 2 (Completed)
- Win/Billing Notifications:
  - POST /api/notify/win/{bid_id} - Win notification callback
  - POST /api/notify/billing/{bid_id} - Billing notification
  - Automatic campaign stats update on win
  - Win rate tracking for bid shading

- Budget Pacing:
  - Even pacing algorithm (24-hour distribution)
  - Hourly budget enforcement
  - GET /api/pacing/status - Monitor all campaigns
  - POST /api/pacing/reset-all - Reset daily budgets
  - Overpacing/underpacing detection

- Campaign Performance Reporting:
  - GET /api/reports/summary - Overall performance
  - GET /api/reports/campaign/{id} - Per-campaign analytics
  - Reports page with interactive charts
  - Date range filtering (1d, 7d, 30d)
  - Campaign breakdown table

- Bid Shading:
  - Automatic bid price optimization
  - Target win rate configuration
  - Learning rate adjustment
  - Min/max shade factor bounds
  - Real-time factor updates based on wins

### Phase 3 (Completed - December 2025)
- Frequency Capping:
  - In-memory storage via MongoDB user_frequencies collection
  - Max impressions per user/day/total limits
  - Time window configuration
  - UI tab in campaign form with toggle and inputs
  - Bid endpoint checks frequency limits before bidding

- Supply Path Optimization (SPO):
  - Preferred/blocked SSP lists
  - Max supply chain hops filtering
  - Bid adjustment factor for preferred paths
  - Authorized sellers requirement option
  - GET /api/spo/analyze/{campaign_id} - Supply path analysis
  - UI tab with full configuration controls

- ML-Based Bid Prediction:
  - Heuristic-based model using historical win/loss data
  - Feature weights for device type, geo, bid floor
  - Prediction weight blending with base price
  - Minimum data points threshold
  - GET /api/ml/stats/{campaign_id} - Model statistics
  - POST /api/ml/train/{campaign_id} - Train from historical data
  - UI tab with configuration options

- Custom Report Exports:
  - GET /api/reports/export/csv - Download reports as CSV
  - GET /api/reports/export/json - Download reports as JSON
  - Date range and campaign filtering

- API Key Auth Removal from Bid Endpoint:
  - POST /api/bid now accepts requests without X-API-Key header
  - Open endpoint for SSP integration

## Prioritized Backlog

### P0 - Completed
- [x] Core bidding engine
- [x] Campaign targeting
- [x] API key authentication
- [x] Dashboard analytics
- [x] Win notification callbacks
- [x] Budget pacing algorithms
- [x] Performance reporting
- [x] Bid shading optimization
- [x] Frequency capping
- [x] Supply path optimization
- [x] ML-based bid prediction
- [x] Report exports (CSV/JSON)

### P1 - Upcoming
- [ ] UI for ML Model Management page (view models, trigger retraining)
- [ ] Multi-currency support
- [ ] Real-time dashboard WebSocket updates

### P2 - Future
- [ ] Advanced fraud detection
- [ ] Viewability prediction
- [ ] A/B testing framework
- [ ] Custom audience segments
- [ ] Native and audio ad format expansion
- [ ] Advanced analytics with drill-down

## Key API Endpoints

### Bidding
- `POST /api/bid` - Main bid endpoint (no auth required)

### Campaigns
- `GET/POST /api/campaigns` - List/create campaigns
- `GET/PUT/DELETE /api/campaigns/{id}` - Single campaign operations
- `POST /api/campaigns/{id}/activate|pause` - Status changes

### Reporting
- `GET /api/reports/summary` - Overall stats
- `GET /api/reports/campaign/{id}` - Campaign details
- `GET /api/reports/export/csv` - CSV export
- `GET /api/reports/export/json` - JSON export

### Advanced Features
- `GET /api/pacing/status` - Budget pacing status
- `GET /api/ml/stats/{campaign_id}` - ML statistics
- `POST /api/ml/train/{campaign_id}` - Train ML model
- `GET /api/spo/analyze/{campaign_id}` - SPO analysis
- `GET /api/frequency/{campaign_id}/{user_id}` - User frequency

## Tech Stack
- **Backend**: FastAPI, Motor (async MongoDB), Pydantic
- **Frontend**: React, Tailwind CSS, Shadcn/UI, Recharts, Axios
- **Database**: MongoDB
- **Domain**: Ad-Tech, OpenRTB, Programmatic Advertising
