# Backend API (New)

Clean backend API for the new frontend. To be implemented.

## Stack

TBD - FastAPI recommended for:
- Better performance than Flask
- Automatic API documentation (OpenAPI/Swagger)
- Built-in data validation with Pydantic
- Async support for database queries

## Planned Features

- Player stats endpoints (leverages existing NFL stats data)
- Team data endpoints (ESPN, Sleeper)
- Historical data queries
- Real-time stats updates
- Authentication/authorization
- Cloud deployment ready (PostgreSQL, Railway/Render)

## Shared Resources

This backend will use the shared resources:
- `../scrapers/` - Data scraping logic
- `../data/` - Database and cached JSON
- `../scripts/` - Utility scripts for data population
