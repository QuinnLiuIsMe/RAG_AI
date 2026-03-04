import { Stack, StackProps } from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

export interface NetworkStackProps extends StackProps {
  useExistingVpc: boolean;
  vpcId?: string;
  publicSubnetIds: string[];
  privateSubnetIds: string[];
  maxAzs: number;
  natGateways: number;
}

export class NetworkStack extends Stack {
  public readonly vpc: ec2.IVpc;
  public readonly privateSubnets: ec2.ISubnet[];

  constructor(scope: Construct, id: string, props: NetworkStackProps) {
    super(scope, id, props);

    if (props.useExistingVpc) {
      if (!props.vpcId) {
        throw new Error('useExistingVpc=true requires vpcId');
      }
      if (props.publicSubnetIds.length === 0 || props.privateSubnetIds.length === 0) {
        throw new Error('useExistingVpc=true requires both publicSubnetIds and privateSubnetIds');
      }

      this.vpc = ec2.Vpc.fromVpcAttributes(this, 'Vpc', {
        vpcId: props.vpcId,
        availabilityZones: Stack.of(this).availabilityZones,
        publicSubnetIds: props.publicSubnetIds,
        privateSubnetIds: props.privateSubnetIds,
      });

      this.privateSubnets = props.privateSubnetIds.map((subnetId, index) =>
        ec2.Subnet.fromSubnetId(this, `PrivateSubnet${index}`, subnetId),
      );
      return;
    }

    const vpc = new ec2.Vpc(this, 'Vpc', {
      maxAzs: props.maxAzs,
      natGateways: props.natGateways,
      subnetConfiguration: [
        {
          name: 'public',
          subnetType: ec2.SubnetType.PUBLIC,
          cidrMask: 24,
        },
        {
          name: 'private-egress',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
          cidrMask: 24,
        },
      ],
    });

    this.vpc = vpc;
    this.privateSubnets = vpc.privateSubnets;
  }
}
