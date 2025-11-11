import { Amplify } from 'aws-amplify';

const amplifyConfig = {
  API: {
    GraphQL: {
      endpoint: process.env.REACT_APP_AMPLIFY_GRAPHQL_ENDPOINT || 'http://localhost:5001/graphql', // Fallback to local
      region: process.env.REACT_APP_AWS_REGION || 'us-east-1',
      defaultAuthMode: process.env.REACT_APP_AMPLIFY_API_KEY ? 'apiKey' : 'none',
      ...(process.env.REACT_APP_AMPLIFY_API_KEY && {
        apiKey: process.env.REACT_APP_AMPLIFY_API_KEY
      })
    }
  }
};

// Only configure Amplify if we have a real endpoint (not the placeholder)
if (process.env.REACT_APP_AMPLIFY_GRAPHQL_ENDPOINT && 
    !process.env.REACT_APP_AMPLIFY_GRAPHQL_ENDPOINT.includes('your-amplify-endpoint')) {
  Amplify.configure(amplifyConfig);
}

export default amplifyConfig;