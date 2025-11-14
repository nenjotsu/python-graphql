#!/bin/bash

# Install dependencies
pip install alembic asyncpg

# Initialize Alembic
alembic init alembic

# Edit alembic/env.py (as shown above)

# Create initial migration
alembic revision --autogenerate -m "Create users table"

# Apply migration
alembic upgrade head

# Check current version
alembic current

# Show migration history
alembic history