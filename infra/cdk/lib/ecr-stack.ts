import { CfnOutput, RemovalPolicy, Stack, StackProps } from 'aws-cdk-lib';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import { Construct } from 'constructs';

export interface EcrStackProps extends StackProps {
  projectName: string;
  repositoryName: string;
}

export class EcrStack extends Stack {
  public readonly repository: ecr.Repository;

  constructor(scope: Construct, id: string, props: EcrStackProps) {
    super(scope, id, props);

    this.repository = new ecr.Repository(this, 'BackendRepository', {
      repositoryName: props.repositoryName,
      imageScanOnPush: true,
      removalPolicy: RemovalPolicy.DESTROY,
      emptyOnDelete: true,
    });

    new CfnOutput(this, 'EcrRepositoryName', {
      value: this.repository.repositoryName,
      exportName: `${props.projectName}-ecr-repository-name`,
    });

    new CfnOutput(this, 'EcrRepositoryUri', {
      value: this.repository.repositoryUri,
      exportName: `${props.projectName}-ecr-repository-uri`,
    });
  }
}
