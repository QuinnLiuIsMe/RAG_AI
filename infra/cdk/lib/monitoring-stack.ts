import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as cloudwatch_actions from 'aws-cdk-lib/aws-cloudwatch-actions';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as sns_subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';
import { Construct } from 'constructs';

export interface MonitoringStackProps extends StackProps {
  projectName: string;
  alarmEmail: string;
  loadBalancer: elbv2.IApplicationLoadBalancer;
  targetGroup: elbv2.IApplicationTargetGroup;
  service: ecs.FargateService;
}

export class MonitoringStack extends Stack {
  constructor(scope: Construct, id: string, props: MonitoringStackProps) {
    super(scope, id, props);

    const alertsTopic = new sns.Topic(this, 'AlertsTopic', {
      displayName: `${props.projectName} alerts`,
      topicName: `${props.projectName}-alerts`,
    });

    if (props.alarmEmail.trim() !== '') {
      alertsTopic.addSubscription(new sns_subscriptions.EmailSubscription(props.alarmEmail));
    }

    const alb5xxAlarm = new cloudwatch.Alarm(this, 'Alb5xxAlarm', {
      alarmName: `${props.projectName}-alb-5xx`,
      metric: props.targetGroup.metricHttpCodeTarget(elbv2.HttpCodeTarget.TARGET_5XX_COUNT, {
        statistic: 'Sum',
        period: Duration.minutes(1),
      }),
      threshold: 5,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
    });

    const latencyAlarm = new cloudwatch.Alarm(this, 'AlbLatencyAlarm', {
      alarmName: `${props.projectName}-alb-latency`,
      metric: props.targetGroup.metricTargetResponseTime({
        statistic: 'Average',
        period: Duration.minutes(1),
      }),
      threshold: 1.5,
      evaluationPeriods: 2,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
    });

    if (props.alarmEmail.trim() !== '') {
      alb5xxAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(alertsTopic));
      latencyAlarm.addAlarmAction(new cloudwatch_actions.SnsAction(alertsTopic));
    }

    new cloudwatch.Dashboard(this, 'OpsDashboard', {
      dashboardName: `${props.projectName}-ops`,
      widgets: [
        [
          new cloudwatch.GraphWidget({
            title: 'ALB Throughput and 5xx',
            left: [
              props.loadBalancer.metricRequestCount({
                statistic: 'Sum',
                period: Duration.minutes(1),
              }),
              props.targetGroup.metricHttpCodeTarget(elbv2.HttpCodeTarget.TARGET_5XX_COUNT, {
                statistic: 'Sum',
                period: Duration.minutes(1),
              }),
            ],
          }),
          new cloudwatch.GraphWidget({
            title: 'ECS CPU and Memory Utilization',
            left: [
              props.service.metricCpuUtilization({
                statistic: 'Average',
                period: Duration.minutes(1),
              }),
              props.service.metricMemoryUtilization({
                statistic: 'Average',
                period: Duration.minutes(1),
              }),
            ],
          }),
        ],
      ],
    });
  }
}
