#!/bin/bash
# Setup script for Korinsic AI Observability with OpenInference

echo "🚀 Setting up Korinsic AI Observability with OpenInference"
echo "=========================================================="

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "   It's recommended to run this in a virtual environment"
    echo "   Run: python -m venv venv && source venv/bin/activate"
    echo ""
fi

echo "📦 Installing OpenInference dependencies..."

# Install the new dependencies
pip install openinference-instrumentation==0.1.12
pip install openinference-semantic-conventions==0.1.9

# Optional: Install Arize Phoenix for advanced AI observability UI
read -p "🤔 Install Arize Phoenix for advanced AI observability UI? (y/N): " install_phoenix
if [[ $install_phoenix =~ ^[Yy]$ ]]; then
    pip install arize-phoenix==4.0.0
    echo "✅ Arize Phoenix installed"
else
    echo "⏭️  Skipping Arize Phoenix installation"
fi

echo ""
echo "🔧 Setting up environment variables..."

# Create or update .env file
if [[ ! -f .env ]]; then
    echo "Creating .env file..."
    cat > .env << 'ENVEOF'
# OpenTelemetry Configuration
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=korinsic-ai-surveillance
OTEL_SERVICE_VERSION=1.0.0

# AI Observability Settings
KORINSIC_AI_OBSERVABILITY_ENABLED=true
KORINSIC_AI_METRICS_ENABLED=true
ENVEOF
    echo "✅ Created .env file with OpenTelemetry settings"
else
    echo "📝 .env file exists - you may need to add these settings manually:"
    echo "   OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317"
    echo "   OTEL_SERVICE_NAME=korinsic-ai-surveillance"
    echo "   OTEL_SERVICE_VERSION=1.0.0"
fi

echo ""
echo "🧪 Testing the installation..."

# Run the test script
if python test_ai_observability.py; then
    echo ""
    echo "✅ Installation and setup completed successfully!"
    echo ""
    echo "�� What's been set up:"
    echo "   • OpenInference instrumentation added to Bayesian engine"
    echo "   • AI-specific tracing for insider dealing analysis"
    echo "   • Evidence mapping and fallback usage tracking"
    echo "   • Performance metrics for inference operations"
    echo "   • Complete API endpoint tracing"
    echo ""
    echo "�� Next steps:"
    echo "   1. Start your OTLP collector (if not running):"
    echo "      docker run -p 4317:4317 otel/opentelemetry-collector"
    echo ""
    echo "   2. Start the Korinsic application:"
    echo "      python src/app.py"
    echo ""
    echo "   3. Make API calls and check your observability dashboard"
    echo ""
    echo "   4. Look for traces with AI-specific attributes like:"
    echo "      • ai.risk.score"
    echo "      • ai.evidence.count" 
    echo "      • ai.inference.latency_ms"
    echo "      • ai.fallback.used"
else
    echo ""
    echo "❌ Test failed - please check the errors above"
    echo "   You may need to install additional dependencies or fix configuration issues"
    exit 1
fi
