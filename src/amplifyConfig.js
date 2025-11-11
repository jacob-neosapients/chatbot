import { Amplify } from 'aws-amplify';

const amplifyConfig = {
  API: {
    GraphQL: {
      endpoint: process.env.REACT_APP_AMPLIFY_GRAPHQL_ENDPOINT || 'https://your-amplify-endpoint.amazonaws.com/graphql',
      region: process.env.REACT_APP_AWS_REGION || 'us-east-1',
      defaultAuthMode: 'apiKey',
      apiKey: process.env.REACT_APP_AMPLIFY_API_KEY || 'your-api-key'
    }
  }
};

Amplify.configure(amplifyConfig);

export default amplifyConfig;