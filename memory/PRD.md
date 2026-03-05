# OpenRTB 2.5/2.6 Bidder with Campaign Manager - PRD

## Original Problem Statement
Build a Demand-Side Platform (DSP) Bidder that handles OpenRTB 2.5/2.6 bid requests, manages campaigns with comprehensive targeting, and provides real-time bidding decisions.

## Architecture
- **Backend**: FastAPI + MongoDB
- **Frontend**: React + Tailwind + Shadcn
- **Bidding Engine**: Real-time matching with targeting rules
- **Protocol Handler**: Version detection, field migration

## Implemented Features

### Phase 1 - Core MVP
- OpenRTB parser with 2.5/2.6 version detection
- Campaign Manager APIs (CRUD, activate/pause)
- Creative Management (banner/video/native/audio)
- SSP Endpoint Management
- Bid endpoint with targeting engine
- Dark theme dashboard with charts

### Phase 2 - Advanced Bidding
- Win/Billing notification callbacks
- Budget pacing (even distribution)
- Campaign performance reporting
- Bid shading (automatic price optimization)

### Phase 3 - Optimization Features
- Frequency capping (in-memory via MongoDB)
- Supply Path Optimization (SPO)
- ML-based bid prediction (heuristic model)
- Custom report exports (CSV/JSON)

### Phase 4 - Insights & Management
- Campaign Performance Insights with health scores
- ML Model Management page
- Multi-Currency Support (USD, EUR, GBP, CAD, AUD, JPY)

### Phase 5 - Enhanced Targeting
- Ad Placements (In-App, In-Stream, Interstitial, etc.)
- Geo Targeting with Lat/Long/Radius
- Device Targeting with carriers by country
- Video Targeting with full dropdowns
- SSP ORTB version selector
- Theme toggle (Dark/Light mode)
- Creative preview functionality

### Phase 6 - Advanced Platform Features
- **Campaign Comparison Tool** - Compare 2-3 campaigns side-by-side
- **A/B Testing Framework** - Split test campaigns with traffic allocation
- **Fraud Detection** - Bot detection, invalid geo filtering
- **Viewability Prediction** - Device/placement impact scoring
- **Custom Audience Segments** - Rule-based targeting
- **Real-Time Bid Stream** - Live bid activity feed

### Phase 7 - SSP Identification & Auth Removal (December 2025)
- **X-API-Key Authentication Removed** from bid endpoint
- **SSP Identification via Unique URLs**
  - Each SSP gets unique endpoint: `/api/bid/{ssp_name}`
  - Generic endpoint `/api/bid` still available for untracked traffic
  - Invalid SSP names return 404
  - Inactive SSPs return 403
- **UI Updates**
  - SSP Endpoints page shows unique URL for each SSP
  - Copy button for each endpoint URL
  - "No authentication required" message
  - All API key UI elements removed

## Key API Endpoints

### Bidding (NO AUTH REQUIRED)
- `POST /api/bid/{ssp_name}` - SSP-specific bid endpoint (tracked)
- `POST /api/bid` - Generic bid endpoint (untracked)

### Campaigns
- `GET/POST /api/campaigns` - List/create campaigns
- `POST /api/campaigns/compare` - Compare campaigns (JSON body)

### A/B Testing
- `GET/POST /api/ab-tests` - List/create tests
- `PUT /api/ab-tests/{id}/status` - Update status

### Fraud Detection
- `GET /api/fraud/stats` - Fraud statistics
- `POST /api/fraud/check` - Check request for fraud

### Audiences
- `GET/POST /api/audiences` - List/create segments

### Real-Time
- `GET /api/bid-stream` - Live bid activity (last 50)

## Navigation Pages
- Dashboard
- Campaigns
- Compare (`/campaigns/compare`)
- Creatives
- SSP Endpoints
- Bid Logs
- Bid Stream (`/bid-stream`)
- Reports
- Budget Pacing
- Insights
- ML Models
- A/B Testing (`/ab-testing`)
- Fraud (`/fraud-detection`)
- Audiences (`/audiences`)
- Migration

## Prioritized Backlog

### Completed
- [x] All core bidding features
- [x] Campaign management
- [x] Advanced targeting
- [x] ML prediction
- [x] Campaign comparison
- [x] A/B testing
- [x] Fraud detection
- [x] Custom audiences
- [x] Real-time bid stream
- [x] X-API auth removal
- [x] SSP identification via unique URLs

### P1 - Upcoming
- [ ] Intelligent Campaign Creation Wizard
- [ ] Real-Time Creative Preview System
- [ ] WebSocket for live updates (replace polling)

### P2 - Future
- [ ] Advanced Creative Editor
- [ ] Automated bid optimization
- [ ] Cross-campaign attribution
- [ ] Server.py refactoring (split into routers)
- [ ] CampaignForm.jsx refactoring (multi-step wizard)

## Tech Stack
- **Backend**: FastAPI, Motor (async MongoDB), Pydantic
- **Frontend**: React, Tailwind CSS, Shadcn/UI, Recharts, Axios
- **Database**: MongoDB
- **Domain**: Ad-Tech, OpenRTB, Programmatic Advertising
