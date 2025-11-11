import { defineBackend } from '@aws-amplify/backend';
import { data } from './data/resource';
import { auth } from './auth/resource';
import { Stack, Duration, RemovalPolicy, CfnOutput } from 'aws-cdk-lib';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as ec2 from 'aws-cdk-lib/aws-ec2';

const backend = defineBackend({
  data,
  auth,
});

// Create Aurora Serverless MySQL cluster with no backups and no maintenance
const dataStack = Stack.of(backend.data);

// Create VPC for the database
const vpc = new ec2.Vpc(dataStack, 'AuroraVPC', {
  maxAzs: 2,
  natGateways: 0, // No NAT gateways to save costs
});

// Create Aurora Serverless v2 cluster with minimal configuration
const dbCluster = new rds.DatabaseCluster(dataStack, 'AuroraCluster', {
  engine: rds.DatabaseClusterEngine.auroraMysql({
    version: rds.AuroraMysqlEngineVersion.VER_3_04_0,
  }),
  writer: rds.ClusterInstance.serverlessV2('writer', {
    autoMinorVersionUpgrade: false, // Disable automatic version upgrades
  }),
  vpc,
  // DISABLE BACKUPS
  backup: {
    retention: Duration.days(1), // Minimum is 1 day, set to 1 for minimal backup
  },
  // DISABLE MAINTENANCE WINDOWS - set to a time that works for you or leave undefined
  preferredMaintenanceWindow: undefined,
  // Database configuration
  defaultDatabaseName: 'neo_guardrails',
  credentials: rds.Credentials.fromGeneratedSecret('admin'), // Auto-generate credentials
  storageEncrypted: false, // Disable encryption to simplify
  removalPolicy: RemovalPolicy.DESTROY, // Allow deletion when stack is destroyed
  deletionProtection: false, // Allow deletion
  serverlessV2MinCapacity: 0.5, // Minimum capacity (scale to zero)
  serverlessV2MaxCapacity: 1, // Maximum capacity (keep it minimal)
});

// Output the database connection details
new CfnOutput(dataStack, 'DatabaseEndpoint', {
  value: dbCluster.clusterEndpoint.hostname,
  description: 'Aurora MySQL cluster endpoint',
});

new CfnOutput(dataStack, 'DatabaseSecretArn', {
  value: dbCluster.secret?.secretArn || '',
  description: 'Secret ARN for database credentials',
});

export default backend;
