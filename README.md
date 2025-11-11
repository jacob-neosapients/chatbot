# Neo-Guardrails

AI Content Safety Classification with real-time moderation powered by DeBERTa v2. Built with React frontend, Amplify Gen 2 backend, and database storage.

[![Built with React](https://img.shields.io/badge/Built%20with-React-61DAFB?style=flat&logo=react)](https://reactjs.org/)
[![Backend](https://img.shields.io/badge/Backend-Amplify%20Gen%202-FF9900?style=flat&logo=aws)](https://aws.amazon.com/amplify/)
[![Database](https://img.shields.io/badge/Database-Aurora%2FMySQL%2FPostgreSQL-4479A1?style=flat&logo=mysql)](https://aws.amazon.com/rds/aurora/)
[![Model](https://img.shields.io/badge/Model-DeBERTa%20v2-FF6F00?style=flat)](https://huggingface.co/docs/transformers/model_doc/deberta-v2)

## Features

- 🛡️ **Real-time Content Moderation**: Instantly classify user input as SAFE or MISUSE
- ⚡ **Fast Inference**: Powered by DeBERTa v2 for quick response times
- 📊 **Confidence Scores**: Get detailed classification metrics
- 🚩 **User Feedback System**: Allow users to flag incorrect classifications
- 📈 **Training Data Collection**: Store interaction data in database for model improvement
- 💬 **Beautiful UI**: Modern, responsive interface with gradient styling
- 🎯 **Performance Metrics**: Track processing time and model statistics
- 🔄 **Real-time Updates**: Live statistics and data synchronization

## Architecture

- **Frontend**: React.js with Amplify client for GraphQL API
- **Backend**: Amplify Gen 2 with AppSync GraphQL API
- **Database**: Aurora/MySQL/PostgreSQL with Amplify Data
- **ML Inference**: Flask API serving the DeBERTa v2 model (can be migrated to Lambda)
- **Authentication**: Amazon Cognito (optional)
- **Real-time**: AWS AppSync subscriptions

## Prerequisites

- Node.js (v18 or higher)
- Python 3.8+ (for ML inference)
- AWS CLI configured
- Amplify CLI installed

## Installation

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd neo-guardrails
npm install
pip install -r requirements.txt
```

### 2. Initialize Amplify

```bash
npx ampx init
```

### 3. Configure Database Connection

Set up your database connection string in AWS Secrets Manager and update the data resource:

```typescript
// amplify/data/resource.ts
import { defineData } from '@aws-amplify/backend';

export const data = defineData({
  schema: a.schema({
    // Your generated schema from existing database
  }),
  authorizationModes: {
    defaultAuthorizationMode: 'apiKey',
  },
});
```

### 4. Generate Schema from Database

```bash
npx ampx generate schema-from-database
```

### 5. Deploy to Sandbox

```bash
npx ampx sandbox
```

## Environment Variables

Create a `.env` file with:

```env
# Amplify Configuration
REACT_APP_AMPLIFY_GRAPHQL_ENDPOINT=https://your-amplify-endpoint.amazonaws.com/graphql
REACT_APP_AWS_REGION=us-east-1
REACT_APP_AMPLIFY_API_KEY=your-api-key

# Flask Backend (for ML inference)
AMPLIFY_GRAPHQL_ENDPOINT=https://your-amplify-endpoint.amazonaws.com/graphql
AMPLIFY_API_KEY=your-api-key
```

## Running the Application

### Development Mode

```bash
# Terminal 1: Start Amplify sandbox
npx ampx sandbox

# Terminal 2: Start Flask backend for ML inference
python app.py

# Terminal 3: Start React frontend
npm start
```

### Production Deployment

```bash
npx ampx deploy
```

## Database Schema

The application uses the following data model:

```typescript
TrainingData: a.model({
  id: a.id().required(),
  timestamp: a.datetime().required(),
  prompt: a.string().required(),
  predictedClass: a.integer().required(),
  label: a.string().required(),
  confidence: a.float().required(),
  processingTime: a.float().required(),
  userFlaggedIncorrect: a.boolean().default(false),
})
```

## API Endpoints

### GraphQL API (Amplify)
- `createTrainingData` - Store classification results
- `updateTrainingData` - Flag classifications as incorrect
- `stats` - Get training data statistics

### REST API (Flask - ML Inference)
- `POST /api/classify` - Classify user prompts
- `GET /api/stats` - Fallback statistics endpoint
- `POST /api/flag` - Fallback flagging endpoint

## Migration Notes

The application supports both Amplify database and JSONL file storage for backward compatibility during migration. The Flask backend will automatically attempt to save to Amplify first, falling back to JSONL files if the GraphQL endpoint is unavailable.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `npm test`
5. Submit a pull request

## License

This project is licensed under the MIT License.
