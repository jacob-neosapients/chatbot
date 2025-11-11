import { defineBackend } from '@aws-amplify/backend';
import { data } from './data/resource';
import { auth } from './auth/resource';

const backend = defineBackend({
  data,
  auth,
});

// Note: Amplify Gen 2 Data with a.schema() uses DynamoDB by default.
// DynamoDB doesn't require maintenance windows or traditional backups.
// Point-in-time recovery and on-demand backups can be configured if needed.
// For production: Consider enabling point-in-time recovery in AWS Console after deployment.

export default backend;