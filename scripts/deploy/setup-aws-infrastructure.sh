#!/bin/bash

# KOR.AI Surveillance Platform - AWS Infrastructure Setup
# This script sets up the complete AWS infrastructure for the application

set -e

# Configuration
STACK_NAME_PREFIX="kor-ai"
AWS_REGION="${AWS_REGION:-us-east-1}"
DOMAIN_NAME="${DOMAIN_NAME:-korinsic.com}"
ENVIRONMENT="${ENVIRONMENT:-staging}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if AWS credentials are configured
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials are not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    log_info "Prerequisites check passed!"
}

# Create SSL certificate
create_ssl_certificate() {
    log_info "Creating SSL certificate for ${DOMAIN_NAME}..."
    
    # Check if certificate already exists
    CERT_ARN=$(aws acm list-certificates \
        --region ${AWS_REGION} \
        --query "CertificateSummaryList[?DomainName=='${DOMAIN_NAME}'].CertificateArn" \
        --output text)
    
    if [ -z "$CERT_ARN" ] || [ "$CERT_ARN" == "None" ]; then
        log_info "Creating new SSL certificate..."
        
        # Request certificate
        CERT_ARN=$(aws acm request-certificate \
            --domain-name ${DOMAIN_NAME} \
            --subject-alternative-names "*.${DOMAIN_NAME}" \
            --validation-method DNS \
            --region ${AWS_REGION} \
            --query 'CertificateArn' \
            --output text)
        
        log_warn "SSL certificate requested. ARN: ${CERT_ARN}"
        log_warn "Please validate the certificate in the AWS Console before proceeding."
        log_warn "This script will wait for certificate validation..."
        
        # Wait for certificate validation
        aws acm wait certificate-validated \
            --certificate-arn ${CERT_ARN} \
            --region ${AWS_REGION}
        
        log_info "SSL certificate validated successfully!"
    else
        log_info "Using existing SSL certificate: ${CERT_ARN}"
    fi
    
    echo $CERT_ARN
}

# Deploy infrastructure stack
deploy_infrastructure() {
    local cert_arn=$1
    local stack_name="${STACK_NAME_PREFIX}-infrastructure-${ENVIRONMENT}"
    
    log_info "Deploying infrastructure stack: ${stack_name}..."
    
    aws cloudformation deploy \
        --template-file deployment/aws-infrastructure.yml \
        --stack-name ${stack_name} \
        --parameter-overrides \
            Environment=${ENVIRONMENT} \
            DomainName=${DOMAIN_NAME} \
            CertificateArn=${cert_arn} \
        --capabilities CAPABILITY_IAM \
        --region ${AWS_REGION}
    
    log_info "Infrastructure stack deployed successfully!"
    
    # Get stack outputs
    ECR_URI=$(aws cloudformation describe-stacks \
        --stack-name ${stack_name} \
        --region ${AWS_REGION} \
        --query 'Stacks[0].Outputs[?OutputKey==`ECRRepositoryURI`].OutputValue' \
        --output text)
    
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name ${stack_name} \
        --region ${AWS_REGION} \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text)
    
    log_info "ECR Repository URI: ${ECR_URI}"
    log_info "Load Balancer DNS: ${ALB_DNS}"
    
    # Export variables for use in CI/CD
    echo "ECR_REPOSITORY_URI=${ECR_URI}" >> infrastructure.env
    echo "ALB_DNS_NAME=${ALB_DNS}" >> infrastructure.env
}

# Setup ECR repository and push initial image
setup_ecr() {
    local ecr_uri=$1
    
    log_info "Setting up ECR repository..."
    
    # Get ECR login token
    aws ecr get-login-password --region ${AWS_REGION} | \
        docker login --username AWS --password-stdin ${ecr_uri%/*}
    
    log_info "Building and pushing initial Docker image..."
    
    # Build Docker image
    docker build -t kor-ai-core:latest .
    
    # Tag for ECR
    docker tag kor-ai-core:latest ${ecr_uri}:latest
    docker tag kor-ai-core:latest ${ecr_uri}:$(git rev-parse --short HEAD)
    
    # Push to ECR
    docker push ${ecr_uri}:latest
    docker push ${ecr_uri}:$(git rev-parse --short HEAD)
    
    log_info "Docker image pushed successfully!"
}

# Setup Amplify app
setup_amplify() {
    log_info "Setting up AWS Amplify application..."
    
    # Get GitHub repository URL
    GITHUB_REPO=$(git config --get remote.origin.url | sed 's/\.git$//')
    
    if [[ $GITHUB_REPO == *"github.com"* ]]; then
        # Extract owner and repo name
        REPO_PARTS=$(echo $GITHUB_REPO | sed 's/.*github\.com[\/:]//; s/\.git$//')
        
        log_info "GitHub repository: ${REPO_PARTS}"
        
        # Create Amplify app
        APP_ID=$(aws amplify create-app \
            --name "kor-ai-${ENVIRONMENT}" \
            --repository ${GITHUB_REPO} \
            --platform WEB \
            --build-spec '{
                "version": 1,
                "frontend": {
                    "phases": {
                        "preBuild": {
                            "commands": ["npm ci"]
                        },
                        "build": {
                            "commands": ["npm run build"]
                        }
                    },
                    "artifacts": {
                        "baseDirectory": "dist",
                        "files": ["**/*"]
                    },
                    "cache": {
                        "paths": ["node_modules/**/*"]
                    }
                }
            }' \
            --environment-variables VITE_API_BASE_URL="https://api-${ENVIRONMENT}.${DOMAIN_NAME}" \
            --query 'app.appId' \
            --output text)
        
        log_info "Amplify app created with ID: ${APP_ID}"
        
        # Create branch
        aws amplify create-branch \
            --app-id ${APP_ID} \
            --branch-name ${ENVIRONMENT} \
            --framework React
        
        log_info "Amplify branch created for ${ENVIRONMENT}"
        
        # Add custom domain if production
        if [ "$ENVIRONMENT" == "production" ]; then
            aws amplify create-domain-association \
                --app-id ${APP_ID} \
                --domain-name ${DOMAIN_NAME} \
                --sub-domain-settings prefix=www,branchName=main
        fi
        
        echo "AMPLIFY_APP_ID=${APP_ID}" >> infrastructure.env
    else
        log_warn "Not a GitHub repository. Skipping Amplify setup."
    fi
}

# Main execution
main() {
    log_info "Starting KOR.AI AWS Infrastructure Setup..."
    log_info "Environment: ${ENVIRONMENT}"
    log_info "Domain: ${DOMAIN_NAME}"
    log_info "Region: ${AWS_REGION}"
    
    check_prerequisites
    
    # Create SSL certificate
    CERT_ARN=$(create_ssl_certificate)
    
    # Deploy infrastructure
    deploy_infrastructure $CERT_ARN
    
    # Get ECR URI from the output
    ECR_URI=$(grep "ECR_REPOSITORY_URI" infrastructure.env | cut -d'=' -f2)
    
    # Setup ECR and push image
    setup_ecr $ECR_URI
    
    # Setup Amplify
    setup_amplify
    
    log_info "Infrastructure setup completed successfully!"
    log_info "Environment variables saved to infrastructure.env"
    log_info ""
    log_info "Next steps:"
    log_info "1. Set up GitHub Secrets with the values from infrastructure.env"
    log_info "2. Configure DNS records for your domain"
    log_info "3. Push to main/develop branch to trigger deployments"
}

# Run main function
main "$@"