#!/bin/bash

alembic revision --autogenerate -m "Description of changes"

alembic upgrade head