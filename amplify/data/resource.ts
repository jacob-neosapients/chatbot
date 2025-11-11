import { defineData } from '@aws-amplify/backend';
import { a } from '@aws-amplify/backend/a';

const schema = a.schema({
  TrainingData: a.model({
    id: a.id().required(),
    timestamp: a.datetime().required(),
    prompt: a.string().required(),
    predictedClass: a.integer().required(),
    label: a.string().required(),
    confidence: a.float().required(),
    processingTime: a.float().required(),
    userFlaggedIncorrect: a.boolean().default(false),
  }).authorization((allow) => [
    allow.publicApiKey().to(['read']),
    allow.authenticated().to(['read', 'create', 'update']),
  ]),

  Stats: a.query()
    .arguments({
      dummy: a.string(),
    })
    .returns(
      a.json()
    )
    .handler(
      a.handler.function('statsFunction')
    )
    .authorization((allow) => [
      allow.publicApiKey().to(['read']),
    ]),
}).authorization((allow) => [
  allow.publicApiKey(),
  allow.authenticated(),
]);

export const data = defineData({
  schema,
  authorizationModes: {
    defaultAuthorizationMode: 'apiKey',
    apiKeyAuthorizationMode: {
      expiresInDays: 30,
    },
  },
});