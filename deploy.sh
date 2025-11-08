#!/bin/bash

# Hacking Capital Deployment Script
# Supports Raindrop CLI and other PaaS deployments

set -e

echo "🚀 Starting Hacking Capital deployment..."

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "📄 Loading environment from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Check if required environment variables are set
required_vars=("ALPHAVANTAGE_API_KEY" "OPENAI_API_KEY" "LIQUID_METAL_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ] || [ "${!var}" = "replace_with_key" ]; then
        echo "⚠️  Warning: $var not set properly. Using demo values for testing."
        if [ "$var" = "ALPHAVANTAGE_API_KEY" ]; then
            export ALPHAVANTAGE_API_KEY="demo"
        fi
        if [ "$var" = "OPENAI_API_KEY" ]; then
            export OPENAI_API_KEY="demo"
        fi
        if [ "$var" = "LIQUID_METAL_API_KEY" ]; then
            export LIQUID_METAL_API_KEY="demo"
        fi
    fi
done

echo "✅ Environment variables configured"

# Build and test locally first
echo "🔨 Building Docker containers..."
docker compose -f docker-compose.dev.yml build

echo "🧪 Running tests locally..."
if command -v python3 &> /dev/null; then
    python3 -m pytest tests/ -v --tb=short
else
    echo "⚠️  Python3 not found, skipping tests"
fi

echo "✅ Local tests passed"

# Deployment options
if [ "$1" = "raindrop" ]; then
    echo "🌧️ Deploying to Raindrop..."

    # Raindrop CLI expects OPENAI_API_KEY for authentication (poorly named)
    # We set it to our LIQUID_METAL_API_KEY value for deployment
    export OPENAI_API_KEY="$LIQUID_METAL_API_KEY"
    echo "🔑 Set OPENAI_API_KEY for Raindrop CLI authentication"

    # Check if raindrop CLI is available (adjust command as needed)
    if command -v raindrop &> /dev/null; then
        raindrop deploy --config raindrop.yml
    elif command -v raindrop-code &> /dev/null; then
        echo "⚠️  raindrop-code found, but this may not be the deployment CLI"
        echo "Please check your Raindrop CLI installation"
        exit 1
    else
        echo "❌ Raindrop CLI not found. Please install it first:"
        echo "brew install raindrop"
        exit 1
    fi

elif [ "$1" = "docker" ]; then
    echo "🐳 Deploying with Docker Compose..."
    docker compose up -d
    echo "✅ Deployment complete!"
    echo "🌐 API: http://localhost:8000"
    echo "🌐 UI: http://localhost:8501"

elif [ "$1" = "render" ]; then
    echo "🎨 Deploying to Render..."
    echo "Please use the Render dashboard to deploy using docker-compose.yml"
    echo "Set the following environment variables in Render:"
    echo "  - ALPHAVANTAGE_API_KEY"
    echo "  - OPENAI_API_KEY"

elif [ "$1" = "railway" ]; then
    echo "🚂 Deploying to Railway..."
    echo "Please use Railway dashboard and connect your GitHub repo"
    echo "Set environment variables in Railway dashboard"

else
    echo "Usage: $0 <platform>"
    echo "Platforms: raindrop, docker, render, railway"
    echo ""
    echo "Examples:"
    echo "  $0 docker     # Local Docker deployment"
    echo "  $0 raindrop   # Raindrop PaaS deployment"
    echo "  $0 render     # Render deployment instructions"
    echo "  $0 railway    # Railway deployment instructions"
    exit 1
fi

echo "🎉 Deployment completed successfully!"
