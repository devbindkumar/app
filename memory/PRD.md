# OpenRTB 2.5/2.6 Bidder with Campaign Manager - PRD

## Original Problem Statement
Build a Demand-Side Platform (DSP) Bidder that handles OpenRTB 2.5/2.6 bid requests, manages campaigns with comprehensive targeting, and provides real-time bidding decisions.

## Architecture
- **Backend**: FastAPI + MongoDB
- **Frontend**: React + Tailwind + Shadcn
- **Bidding Engine**: Real-time matching with targeting rules
- **Protocol Handler**: Version detection, field migration

## Implemented Features

### Phase 1-3 - Core & Optimization
- OpenRTB parser with 2.5/2.6 version detection
- Campaign Manager APIs (CRUD, activate/pause)
- Creative Management (banner/video/native/audio)
- SSP Endpoint Management
- Win/Billing notification callbacks
- Budget pacing, Bid shading
- Frequency capping, SPO, ML-based bid prediction

### Phase 4-5 - Insights & Targeting
- Campaign Performance Insights with health scores
- ML Model Management page
- Multi-Currency Support
- Ad Placements, Geo/Device Targeting
- Theme toggle (Dark/Light mode)
- Creative preview functionality

### Phase 6 - Advanced Platform Features
- Campaign Comparison Tool
- A/B Testing Framework
- Fraud Detection
- Custom Audience Segments
- Real-Time Bid Stream

### Phase 7 - SSP Token Authentication (December 2025)
- **X-API-Key Authentication Removed** from bid endpoint
- **SSP Identification via Unique Tokens**
  - Each SSP gets unique 16-char hex token
  - Endpoint: `/api/bid/{endpoint_token}`
  - Invalid tokens return 404, inactive SSPs return 403

### Phase 8 - Analytics & Advanced Features (December 2025)
- **SSP Performance Analytics** (`/ssp-analytics`)
  - Overview stats: total requests, bid rate, win rate, spend
  - SSP rankings table
  - Per-SSP details with response time metrics
  
- **Automated Bid Optimization** (`/bid-optimization`)
  - Enable/disable optimization per campaign
  - Target win rate configuration
  - Auto-adjust bid prices based on performance
  - Optimization history tracking
  
- **Cross-Campaign Attribution** (`/attribution`)
  - Four attribution models: first_touch, last_touch, linear, time_decay
  - User journey tracking
  - Attribution share analysis per campaign
  
- **Advanced Creative Editor** (`/creatives/editor`)
  - Image upload capability (JPG, PNG, GIF, WebP)
  - Live preview for banner/native creatives
  - Template library
  - CTA customization with color picker

## Key API Endpoints

### Bidding (NO AUTH REQUIRED)
- `POST /api/bid/{endpoint_token}` - Token-specific bid endpoint (tracked)
- `POST /api/bid` - Generic bid endpoint (untracked)

### SSP Analytics
- `GET /api/ssp-analytics/overview` - SSP performance overview
- `GET /api/ssp-analytics/{ssp_id}/details` - Per-SSP details
- `POST /api/ssp-endpoints/{id}/regenerate-token` - Regenerate token

### Bid Optimization
- `GET /api/bid-optimization/status` - All campaigns status
- `POST /api/bid-optimization/{id}/enable` - Enable optimization
- `POST /api/bid-optimization/{id}/run` - Run optimization
- `GET /api/bid-optimization/{id}/history` - View history

### Attribution
- `POST /api/attribution/track` - Track attribution event
- `GET /api/attribution/user/{user_id}` - User journey
- `GET /api/attribution/analysis?model={model}` - Analysis

### File Upload
- `POST /api/upload/image` - Upload image
- `GET /api/uploads/{filename}` - Serve image
- `DELETE /api/uploads/{filename}` - Delete image

## Navigation Pages
- Dashboard
- Campaigns, Compare
- Creatives, Creative Editor
- SSP Endpoints, SSP Analytics
- Bid Logs, Bid Stream
- Reports, Budget Pacing
- Insights, ML Models
- Bid Optimizer
- A/B Testing, Fraud
- Audiences, Attribution
- Migration

## Prioritized Backlog

### Completed
- [x] All core bidding features
- [x] Campaign management & targeting
- [x] ML prediction & optimization
- [x] Campaign comparison & A/B testing
- [x] Fraud detection & audiences
- [x] SSP token-based identification
- [x] SSP Performance Analytics
- [x] Automated Bid Optimization
- [x] Cross-Campaign Attribution
- [x] Advanced Creative Editor with image upload

### P1 - Upcoming
- [ ] WebSocket real-time updates for Bid Stream
- [ ] Intelligent Campaign Creation Wizard (refactor CampaignForm.jsx)
- [ ] Real-Time Creative Preview System

### P2 - Future
- [ ] Server.py refactoring (split into modular routers)
- [ ] Advanced fraud detection algorithms
- [ ] Automated campaign optimization recommendations

## Tech Stack
- **Backend**: FastAPI, Motor (async MongoDB), Pydantic
- **Frontend**: React, Tailwind CSS, Shadcn/UI, Recharts, Axios
- **Database**: MongoDB
- **Domain**: Ad-Tech, OpenRTB, Programmatic Advertising

## Latest Updates (December 2025)
- SSP endpoints now use unique 16-char hex tokens instead of names
- Added SSP Performance Analytics dashboard
- Added Automated Bid Optimization with win rate targeting
- Added Cross-Campaign Attribution with 4 models
- Added Advanced Creative Editor with image upload
- All 18 backend tests passing, all frontend pages functional
