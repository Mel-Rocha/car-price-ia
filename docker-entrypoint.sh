#!/bin/bash

echo "Start application"
exec uvicorn main:app --host 0.0.0.0 --port 8000