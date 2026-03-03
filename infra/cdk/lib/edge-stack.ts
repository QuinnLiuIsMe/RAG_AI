import { CfnOutput, Stack, StackProps } from 'aws-cdk-lib';
import * as apigwv2 from 'aws-cdk-lib/aws-apigatewayv2';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import { Construct } from 'constructs';

export interface EdgeStackProps extends StackProps {
  projectName: string;
  loadBalancer: elbv2.IApplicationLoadBalancer;
}

export class EdgeStack extends Stack {
  constructor(scope: Construct, id: string, props: EdgeStackProps) {
    super(scope, id, props);

    const api = new apigwv2.CfnApi(this, 'HttpApi', {
      name: `${props.projectName}-http-api`,
      protocolType: 'HTTP',
    });

    const integration = new apigwv2.CfnIntegration(this, 'AlbIntegration', {
      apiId: api.ref,
      integrationType: 'HTTP_PROXY',
      integrationMethod: 'ANY',
      integrationUri: `http://${props.loadBalancer.loadBalancerDnsName}`,
      payloadFormatVersion: '1.0',
    });

    new apigwv2.CfnRoute(this, 'DefaultRoute', {
      apiId: api.ref,
      routeKey: '$default',
      target: `integrations/${integration.ref}`,
    });

    const stage = new apigwv2.CfnStage(this, 'ApiStage', {
      apiId: api.ref,
      stageName: 'prod',
      autoDeploy: true,
    });

    new CfnOutput(this, 'ApiGatewayInvokeUrl', {
      value: `https://${api.ref}.execute-api.${Stack.of(this).region}.amazonaws.com/${stage.stageName}`,
      exportName: `${props.projectName}-api-gateway-invoke-url`,
    });
  }
}
