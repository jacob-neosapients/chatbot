import { type ClientSchema, a, defineData } from '@aws-amplify/backend';

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
  }).authorization((allow: any) => [
    allow.publicApiKey().to(['read']),
    allow.authenticated().to(['read', 'create', 'update']),
  ]),
}).authorization((allow: any) => [
  allow.publicApiKey(),
  allow.authenticated(),
]);

export type Schema = ClientSchema<typeof schema>;

export const data = defineData({
  schema,
  authorizationModes: {
    defaultAuthorizationMode: 'apiKey',
    apiKeyAuthorizationMode: {
      expiresInDays: 30,
    },
  },
});