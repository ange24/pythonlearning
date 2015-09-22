import uuid, string, random, math
import config
from troposphere import FindInMap, GetAtt, Join, GetAZs, Base64, Parameter, Output, Ref, Select, Tags, Template, autoscaling, elasticache, Output
import troposphere.ec2 as ec2
import troposphere.s3 as S3
import troposphere.elasticloadbalancing as elb
import troposphere.cloudwatch as cloudwatch
import troposphere.cloudformation as cloudFormation
import troposphere.iam as iam
import troposphere.route53 as route53
from uuid import uuid4
template = Template()

RegionMap = template.add_mapping('RegionMap', config.RegionMap)
VpcMap = template.add_mapping('VpcMap', config.VpcMap)
ZoneMap = template.add_mapping("ZoneMap", config.ZoneMap)
StackEnv = template.add_parameter(Parameter(
    "StackEnv",
    Description="What environment",
    Type="String",
    Default="ACC",
    AllowedValues = [ 'ACC', 'PROD' ],
))

SpaceDiskSize = template.add_parameter(Parameter(
    "SpaceDiskSize",
    Description="Disk size for space in GB",
    Type="Number",
    Default="1024",

))
BuildNumber =  template.add_parameter(Parameter(
  "BuildNumber",
  Description="Teamcity build number",
  Type="String"
))
SSHKey = template.add_parameter(Parameter(
    "SSHKey",
    Description="What SSH Key",
    Type="String",
    Default="TradeDoubler",
    AllowedValues = [ 'martin', 'jon' ,'TradeDoubler'],
))
cpuMinInstances = template.add_parameter(Parameter(
  "cpuMinInstances",
  Description="Number of minimum instances in load based autoscaling group",
  Type="Number",
  Default="1"
))
cpuDesiredInstances= template.add_parameter(Parameter(
  "cpuDesiredInstances",
  Description="Number of minimum instances in load based autoscaling group",
  Type="Number",
  Default="1"
))
cpuMaxInstances= template.add_parameter(Parameter(
  "cpuMaxInstances",
  Description="Number of minimum instances in load based autoscaling group",
  Type="Number",
  Default="30"
))
timeInstancesHigh = template.add_parameter(Parameter(
  "timeInstancesHigh",
  Description="Number of instances in time based autoscaling group when high",
  Type="Number",
  Default="2"
))
timeInstancesLow = template.add_parameter(Parameter(
  "timeInstancesLow",
  Description="Number of instances in time based autoscaling group when low",
  Type="Number",
  Default="1"
))
cacheInstances =  template.add_parameter(Parameter(
  "cacheInstances",
  Description="Number of cache instances",
  Type="Number",
  Default="1"
))
spaceInstances =  template.add_parameter(Parameter(
  "spaceInstances",
  Description="Number of spaceInstances",
  Type="Number",
  Default="1"
))
txELB = template.add_parameter(Parameter(
  "txELB",
  Type = "String"
))
txELBPvn = template.add_parameter(Parameter(
  "txELBPvn",
  Type = "String"
))
txELBTbs = template.add_parameter(Parameter(
  "txELBTbs",
  Type = "String"
))
txELBTbl = template.add_parameter(Parameter(
  "txELBTbl",
  Type = "String"
))
PrimarySubnet = template.add_parameter(Parameter(
  "PrimarySubnet",
  Type = "String"
))
SecondarySubnet= template.add_parameter(Parameter(
  "SecondarySubnet",
  Type = "String"
))
txInstanceSG= template.add_parameter(Parameter(
  "txInstanceSG",
  Type = "String"
))
txCacheSG= template.add_parameter(Parameter(
  "txCacheSG",
  Type = "String"
))
txSpaceSG= template.add_parameter(Parameter(
  "txSpaceSG",
  Type = "String"
))
txELBSG= template.add_parameter(Parameter(
  "txELBSG",
  Type = "String"
))
deployProfile= template.add_parameter(Parameter(
  "deployProfile",
  Type = "String"
))


ListenersList = []
for (s,p) in config.CachePorts.items() :
  ListenersList.append(elb.Listener(
    LoadBalancerPort=p,
    InstancePort=p,
    Protocol='TCP',
  ))

cacheELB = template.add_resource(elb.LoadBalancer(
    "cacheELB",
    ConnectionDrainingPolicy=elb.ConnectionDrainingPolicy(
        Enabled=True,
        Timeout=300,
    ),
    Scheme = "internal",
    CrossZone=True,
    Subnets=[Ref(PrimarySubnet),Ref(SecondarySubnet)],
    SecurityGroups=[Ref(txInstanceSG)],
    Listeners=ListenersList,
))

spaceELB = template.add_resource(elb.LoadBalancer(
    "spaceELB",
    ConnectionDrainingPolicy=elb.ConnectionDrainingPolicy(
        Enabled=True,
        Timeout=300,
    ),
    Scheme = "internal",
    CrossZone=True,
    Subnets=[Ref(PrimarySubnet),Ref(SecondarySubnet)],
    SecurityGroups=[Ref(txInstanceSG)],
    Listeners=[
        elb.Listener(
            LoadBalancerPort="4739",
            InstancePort=4739,
            Protocol="TCP",

        )
    ],
    HealthCheck=elb.HealthCheck(
        Target="TCP:5739",
        HealthyThreshold="10",
        UnhealthyThreshold="10",
        Interval="5",
        Timeout="2",
    ),

))

pubkeyList = []
for ( name, key ) in config.SshKeys.items():
  pubkeyList.append('echo "{0}" >> /home/ec2-user/.ssh/authorized_keys2'.format(key))
lcTxHttp = template.add_resource(autoscaling.LaunchConfiguration(
    "lcTxHttp",
    AssociatePublicIpAddress=True,
    KeyName=Ref(SSHKey),
    InstanceType=FindInMap("RegionMap", Ref("AWS::Region"), "TXHttpType"),
    ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
    SecurityGroups=[Ref(txInstanceSG)],
    IamInstanceProfile=Ref(deployProfile),
    BlockDeviceMappings=[
        ec2.BlockDeviceMapping(
            DeviceName="/dev/xvda",
            Ebs=ec2.EBSBlockDevice(
            DeleteOnTermination=True,
            VolumeSize=8,
            VolumeType="gp2",
            ))
    ],
    UserData=Base64(
        Join('\n', [
            "#!/bin/bash",
            "set -e",
            "function ERR() { shutdown now -h; }",
            "trap ERR ERR",
            "echo '10.240.129.146 tdprodapp30' >> /etc/hosts",
            "echo '10.240.129.10 tdprodapp45' >> /etc/hosts",
            "echo '10.240.129.11 tdprodapp46' >> /etc/hosts",
            "echo '10.240.161.10 tdprodapp47' >> /etc/hosts",
            "echo '10.240.161.11 tdprodapp48' >> /etc/hosts",
            "echo '10.240.129.12 tdprodapp67' >> /etc/hosts",
            "echo '10.240.129.13 tdprodapp68' >> /etc/hosts",
            "echo '10.240.3.10 tdaccapp05' >> /etc/hosts",
            "echo '10.240.35.10 tdaccapp09' >> /etc/hosts",
            "echo '10.240.1.12 tdaccapp03' >> /etc/hosts",
            "echo '10.240.33.10 tdaccapp04' >> /etc/hosts",
            "#echo '10.240.193.51 tddbadm' >> /etc/hosts",

            "echo \"127.0.0.1 $(hostname) localhost localhost.localdomain\" >> /etc/hosts",
            "ln -sf /usr/share/zoneinfo/Europe/Stockholm  /etc/localtime",
            Join('\n', pubkeyList),

            "yum -y install puppet awslogs aws-cli-plugin-cloudwatch-logs-1.0.1",
            "yum -y update --security",
             Join("",[
              "export STACK_ENV=",
               Ref(StackEnv),
             ]),
              Join("",[
              "export BUIILD_NUMBER=",
               Ref(BuildNumber),
             ]),
             Join(" ",["aws s3 sync","--region",Ref("AWS::Region"),
               Join("",["s3://deploy.",
                  Ref("AWS::Region"),
                  ".tradedoubler.com/builds/",
                  Ref(BuildNumber),"/"
                  ]),
              "/tmp"]),

            Join("",[
                "sed -i 's/@ENV@/",
                 Ref(StackEnv),
                "/g' /tmp/sources.json",
            ]),
            "yum install -y /tmp/jdk.rpm",

            "adduser hercules",
            "export HERCULES_HOME=/home/hercules",
            Join("",[
            "export HERCULES_DIST=",
              Join("_",[
                Ref(StackEnv),
                Ref("AWS::Region")
              ])
            ]),
            "export HERCULES_SHARED=/export/shared/hercules",
            "export JAVA_HOME=/usr/java/latest",
            "export HERCULES_KEYWORD_DIR=/export/shared/herculesSynch/keyword",
            "mkdir -p $HERCULES_SHARED",
            "mkdir -p $HERCULES_KEYWORD_DIR",
            "mkdir -p $HERCULES_SHARED/conf",
            "mkdir /export/shared/statistics",
            "chown hercules:hercules /export/shared/statistics",
            "chown hercules:hercules $HERCULES_SHARED",
            "chown hercules:hercules $HERCULES_KEYWORD_DIR",
            "chown hercules:hercules $HERCULES_SHARED/conf",
            "chmod 0755 /tmp/hercules-*",
            "su -c \"./tmp/hercules-* -f\" hercules",
            Join("",[
                "sed -i 's/@cachehost@/",
                GetAtt("cacheELB","DNSName"),
                "/g' $HERCULES_HOME/app/conf/services-$HERCULES_DIST.xml",
            ]),
            Join("",[
                "sed -i 's/@txspacehost@/",
                GetAtt("spaceELB","DNSName"),
                "/g' $HERCULES_HOME/app/conf/services-$HERCULES_DIST.xml",
            ]),
            Join("",[
                "sed -i 's/@txspacehost@/",
                GetAtt("spaceELB","DNSName"),
                "/g' $HERCULES_HOME/app/conf/services-$HERCULES_DIST.xml",
            ]),
            "sed -i 's/^AuthorizedKeysFile/#AuthorizedKeysFile/' /etc/ssh/sshd_config",
            "service sshd restart",
            "cp -a $HERCULES_HOME/app/conf/services-$HERCULES_DIST.xml $HERCULES_SHARED/conf",
            "cp -a $HERCULES_HOME/app/conf/services-def.xml $HERCULES_SHARED/conf",

            "su -c \"mkdir -p   $HERCULES_KEYWORD_DIR/uat\" hercules",
            "su -c \"mkdir -p  $HERCULES_KEYWORD_DIR/prod\" hercules",
            "su -c \"aws s3 sync s3://keywordcache.tradedoubler.com $HERCULES_KEYWORD_DIR\" hercules",

            "echo \"0,30 * * * * aws s3 sync --delete s3://keywordcache.tradedoubler.com $HERCULES_KEYWORD_DIR \" > /var/spool/cron/hercules",


            "echo \"0 * * * * yum update --security\" > /var/spool/cron/root",
            "export SERVICE_DEF_FILE=/export/shared/hercules/conf/services-def.xml",
            "export SERVICE_CONFIG_FILE=/export/shared/hercules/conf/services-$HERCULES_DIST.xml",
            "sysctl -w net.ipv4.tcp_max_syn_backlog=5000",
            "sysctl -w net.ipv4.tcp_synack_retries=3",
            "sysctl -w net.ipv4.tcp_syn_retries=3",
            "sysctl -w net.core.somaxconn=512",
            "sysctl -w net.core.optmem_max=81920",
            "sysctl -w net.core.rmem_max=16777216",
            "sysctl -w net.core.wmem_max=16777216",
            "sysctl -w net.ipv4.tcp_rmem='4096 87380 16777216'",
            "su -c \"$HERCULES_HOME/app/bin/herculesService -t start TXServerHttp\" hercules",
            "yum install -y /tmp/SumoCollector-*.x86_64.rpm",
            "chmod 0600 /tmp/sumo-*.conf",
            "mv /tmp/sumo-txhttp.conf /etc/sumo.conf",
            "service collector start",
            "service awslogs start",
            "cd /tmp",
            "tar xzf puppet-nagious.tar.gz",
            "cd puppet_nagios_amazon",
            "puppet apply --modulepath ./modules manifests/site.pp",

        ]),
    ),
))
cacheWaitHandle = template.add_resource(cloudFormation.WaitConditionHandle(
    str(uuid4().int),
))
#Cache script
cacheScript=[
            "#!/bin/bash",
            "set -e",
            "function ERR() { shutdown now -h; }",
            "trap ERR ERR",
            "echo '10.240.129.10 tdprodapp45' >> /etc/hosts",
            "echo '10.240.129.11 tdprodapp46' >> /etc/hosts",
            "echo '10.240.161.10 tdprodapp47' >> /etc/hosts",
            "echo '10.240.161.11 tdprodapp48' >> /etc/hosts",
            "echo '10.240.129.12 tdprodapp67' >> /etc/hosts",
            "echo '10.240.129.13 tdprodapp68' >> /etc/hosts",
            "echo '10.240.129.146 tdprodapp30' >> /etc/hosts",
            "echo '10.240.3.10 tdaccapp05' >> /etc/hosts",
            "echo '10.240.35.10 tdaccapp09' >> /etc/hosts",
            "echo '10.240.1.12 tdaccapp03' >> /etc/hosts",
            "echo '10.240.33.10 tdaccapp04' >> /etc/hosts",
            "echo '10.240.129.24 tdprodapp81' >> /etc/hosts",
            "echo '10.240.1.17 tdaccapp23' >> /etc/hosts",
            "#echo '10.240.193.51 tddbadm' >> /etc/hosts",

            "echo \"127.0.0.1 $(hostname) localhost localhost.localdomain\" >> /etc/hosts",
            "sed -i 's/^Defaults    requiretty/# Defaults    requiretty/g' /etc/sudoers",
            "echo \"nagios ALL=(hercules) NOPASSWD:ALL\" >> /etc/sudoers.d/nagios",
            "ln -sf /usr/share/zoneinfo/Europe/Stockholm  /etc/localtime",
            "yum -y install puppet awslogs aws-cli-plugin-cloudwatch-logs-1.0.1",
            "yum -y update --security",
             Join('\n', pubkeyList),
             Join("",[
              "export STACK_ENV=",
               Ref(StackEnv),
             ]),
            Join("",[
              "export BUIILD_NUMBER=",
               Ref(BuildNumber),
             ]),
            Join("",[
              "export BUIILD_NUMBER=",
               Ref(BuildNumber),
             ]),
                         Join(" ",["aws s3 sync","--region",Ref("AWS::Region"),
               Join("",["s3://deploy.",
                  Ref("AWS::Region"),
                  ".tradedoubler.com/builds/",
                  Ref(BuildNumber),"/"
                  ]),
              "/tmp"]),

              Join("",[
                "sed -i \"s/@ENV@/",
                 Ref(StackEnv),
                "/g\" /tmp/sources.json",
            ]),




            Join("", [
              "export WAIT_HANDLE=\"",
              Ref(cacheWaitHandle),
              "\""
            ]),
            "echo $WAIT_HANDLE",
            "echo $WAIT_HANDLE > /tmp/waithandle",
            "yum install -y /tmp/jdk.rpm",
            "adduser hercules",
            "export HERCULES_HOME=/home/hercules",
            Join("",[
            "export HERCULES_DIST=",
              Join("_",[
                Ref(StackEnv),
                Ref("AWS::Region")
              ])
            ]),
            "export HERCULES_SHARED=/export/shared/hercules",
            "export JAVA_HOME=/usr/java/latest",
            "export HERCULES_KEYWORD_DIR=/export/shared/herculesSynch/keyword",
            "mkdir -p $HERCULES_SHARED",
            "mkdir -p $HERCULES_KEYWORD_DIR",
            "mkdir -p $HERCULES_SHARED/conf",
            "mkdir /export/shared/statistics",
            "chown hercules:hercules /export/shared/statistics",
            "chown hercules:hercules $HERCULES_SHARED",
            "chown hercules:hercules $HERCULES_KEYWORD_DIR",
            "chown hercules:hercules $HERCULES_SHARED/conf",
            "chmod 0755 /tmp/hercules-*",
            "su -c \"./tmp/hercules-* -f\" hercules",
            Join("",[
                "sed -i 's/@cachehost@/",
              "localhost",
                "/g' $HERCULES_HOME/app/conf/services-$HERCULES_DIST.xml",
            ]),
            Join("",[
                "sed -i \"s/@txspacehost@/",
              GetAtt("spaceELB","DNSName"),
                "/g\" $HERCULES_HOME/app/conf/services-$HERCULES_DIST.xml",
            ]),
            "sed -i 's/^AuthorizedKeysFile/#AuthorizedKeysFile/' /etc/ssh/sshd_config",
            "service sshd restart",
            "cp -a $HERCULES_HOME/app/conf/services-$HERCULES_DIST.xml $HERCULES_SHARED/conf",
            "cp -a $HERCULES_HOME/app/conf/services-def.xml $HERCULES_SHARED/conf",

            "echo \"0 * * * * yum update --security\" > /var/spool/cron/root",
            "yum install -y /tmp/SumoCollector-*.x86_64.rpm",
            "chmod 0600 /tmp/sumo-*.conf",
            "mv /tmp/sumo-txcache.conf /etc/sumo.conf",
            "service collector start",
            "service awslogs start",
            "cd /tmp",
            "tar xzf puppet-nagious.tar.gz",
            "cd puppet_nagios_amazon",
            "puppet apply --modulepath ./modules manifests/site.pp",
            "echo \"export JAVA_HOME=$JAVA_HOME\" >> /var/nagios/.bash_profile",
            "echo \"export NAGIOS_HOME=$HERCULES_HOME\" >> /var/nagios/.bash_profile",
            "sed -i 's/app01/home/g' /etc/nagios/nrpe.cfg",
            "service nrpe restart",
#            "echo '0,5,10,15,20,25,30,35,40,45,50,55 * * * * /bin/bash <( echo \"df | egrep 'xvd' | tr -s [:space:] | cut -f5 -d' ' | sed -e 's/%//g'\")' >> /var/spool/cron/root"
#            "echo \"0,5,10,15,20,25,30,35,40,45,50,55 * * * * cloudwatch put-metric-data --metric-name --namespace PROD --value $( /home/hercules/app/bin/checkHercules.sh )\" >> /var/spool/cron/hercules",

]

for ( service, port ) in config.CachePorts.items():
  cacheScript.append("su -c \". $HERCULES_HOME/.bashrc;  $HERCULES_HOME/app/bin/herculesService -t start {0}\" hercules".format(service))

lcCache = template.add_resource(autoscaling.LaunchConfiguration(
    "lcCache",
    AssociatePublicIpAddress=True,
    KeyName=Ref(SSHKey),
    InstanceType=FindInMap("RegionMap", Ref("AWS::Region"), "TXCacheType"),
    ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
    SecurityGroups=[Ref(txCacheSG)],
    IamInstanceProfile=Ref("deployProfile"),
    BlockDeviceMappings=[
        ec2.BlockDeviceMapping(
            DeviceName="/dev/xvda",
            Ebs=ec2.EBSBlockDevice(
            DeleteOnTermination=True,
            VolumeSize=8,
            VolumeType="gp2",
            ))
    ],
    UserData=Base64(
        Join('\n', cacheScript),
    ),
))


# mountpoint $HERCULES_HOME/data/tx_space
lcSpace = template.add_resource(autoscaling.LaunchConfiguration(
    "lcSpace",

    AssociatePublicIpAddress=True,
    KeyName=Ref(SSHKey),
    InstanceType=FindInMap("RegionMap", Ref("AWS::Region"), "TXSpaceType"),
    ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
    SecurityGroups=[Ref(txSpaceSG)],
    IamInstanceProfile=Ref(deployProfile),

    BlockDeviceMappings=[
        ec2.BlockDeviceMapping(
            DeviceName="/dev/xvda",
            Ebs=ec2.EBSBlockDevice(
            DeleteOnTermination=True,
            VolumeSize=8,
            VolumeType="gp2",
            )),
        ec2.BlockDeviceMapping(
            DeviceName="/dev/xvdb",
            Ebs=ec2.EBSBlockDevice(
            DeleteOnTermination=False,
            VolumeSize=Ref(SpaceDiskSize),
            VolumeType="standard",
            ))
    ],
    UserData=Base64(
        Join('\n', [
            "#!/bin/bash",
            "set -e",
            "function ERR() { shutdown now -h; }",
            "trap ERR ERR",

            "echo '10.240.129.10 tdprodapp45' >> /etc/hosts",
            "echo '10.240.129.11 tdprodapp46' >> /etc/hosts",
            "echo '10.240.161.10 tdprodapp47' >> /etc/hosts",
            "echo '10.240.161.11 tdprodapp48' >> /etc/hosts",
            "echo '10.240.129.12 tdprodapp67' >> /etc/hosts",
            "echo '10.240.129.13 tdprodapp68' >> /etc/hosts",
            "echo '10.240.3.10 tdaccapp05' >> /etc/hosts",
            "echo '10.240.35.10 tdaccapp09' >> /etc/hosts",
            "echo \"127.0.0.1 $(hostname) localhost localhost.localdomain\" >> /etc/hosts",
            "ln -sf /usr/share/zoneinfo/Europe/Stockholm  /etc/localtime",
            Join('\n', pubkeyList),
            "yum -y install puppet awslogs aws-cli-plugin-cloudwatch-logs-1.0.1",
            "yum -y update --security",
             Join("",[
              "export STACK_ENV=",
               Ref(StackEnv),
             ]),
             Join("",[
              "export BUIILD_NUMBER=",
               Ref(BuildNumber),
             ]),
                         Join(" ",["aws s3 sync","--region",Ref("AWS::Region"),
               Join("",["s3://deploy.",
                  Ref("AWS::Region"),
                  ".tradedoubler.com/builds/",
                  Ref(BuildNumber),"/"
                  ]),
              "/tmp"]),

            Join("",[
                "sed -i \"s/@ENV@/",
                 Ref(StackEnv),
                "/g\" /tmp/sources.json",
            ]),

            "yum install -y /tmp/jdk.rpm",
            "adduser hercules",
            "export HERCULES_HOME=/home/hercules",
            Join("",[
            "export HERCULES_DIST=",
              Join("_",[
                Ref(StackEnv),
                Ref("AWS::Region")
              ])
            ]),
            "export HERCULES_SHARED=/export/shared/hercules",
            "export JAVA_HOME=/usr/java/latest",
            "export HERCULES_KEYWORD_DIR=/export/shared/herculesSynch/keyword",
            "mkdir -p $HERCULES_HOME/data",
            "mkdir -p $HERCULES_SHARED",
            "mkdir -p $HERCULES_KEYWORD_DIR",
            "mkdir -p $HERCULES_SHARED/conf",
            "mkdir /export/shared/statistics",
            "chown hercules:hercules /export/shared/statistics",
            "mkfs.ext4 /dev/xvdb",
            "mount /dev/xvdb $HERCULES_HOME/data",
            "chown hercules:hercules $HERCULES_HOME/data",
            "chown hercules:hercules $HERCULES_SHARED",
            "chown hercules:hercules $HERCULES_KEYWORD_DIR",
            "chown hercules:hercules $HERCULES_SHARED/conf",

            "chmod 0755 /tmp/hercules-*",
            "su -c \"./tmp/hercules-* -f\" hercules",
            Join("",[
                "sed -i 's/@cachehost@/",
              GetAtt("cacheELB","DNSName"),
                "/g' $HERCULES_HOME/app/conf/services-$HERCULES_DIST.xml",
            ]),
            Join("",[
                "sed -i \"s/@txspacehost@/",
                 "localhost",
                "/g\" $HERCULES_HOME/app/conf/services-$HERCULES_DIST.xml",
            ]),
            "sed -i 's/^AuthorizedKeysFile/#AuthorizedKeysFile/' /etc/ssh/sshd_config",
            "service sshd restart",
            "cp -a $HERCULES_HOME/app/conf/services-$HERCULES_DIST.xml $HERCULES_SHARED/conf",
            "cp -a $HERCULES_HOME/app/conf/services-def.xml $HERCULES_SHARED/conf",

            "echo \"0 * * * * yum update --security\" > /var/spool/cron/root",
            "su -c \". $HERCULES_HOME/.bashrc; $HERCULES_HOME/app/bin/herculesService -t start TXSpace\" hercules",
            "yum install -y /tmp/SumoCollector-*.x86_64.rpm",
            "chmod 0600 /tmp/sumo-*.conf",
            "mv /tmp/sumo-txspace.conf /etc/sumo.conf",
            "service collector start",
            "service awslogs start",
            "cd /tmp",
            "tar xzf puppet-nagious.tar.gz",
            "cd puppet_nagios_amazon",
            "puppet apply --modulepath ./modules manifests/site.pp",
            "chown hercules:nagios $HERCULES_HOME",
            "chown hercules:nagios $HERCULES_HOME/data",
            "chmod 775 $HERCULES_HOME",
            "chmod 775 $HERCULES_HOME/data",
        ]),
    ),
))



spaceASG = template.add_resource(autoscaling.AutoScalingGroup(
    "spaceASG",
    LaunchConfigurationName=Ref(lcSpace),
    MinSize=Ref(spaceInstances),
    MaxSize="1",
    DesiredCapacity=Ref(spaceInstances),
    AvailabilityZones=[Select(0,(GetAZs(""))),Select(1,(GetAZs("")))],
    VPCZoneIdentifier=[Ref(PrimarySubnet),Ref(SecondarySubnet)],
    LoadBalancerNames=[Ref(spaceELB)],
     Tags=[autoscaling.Tag(
      "td:type" ,"TxSpace", True
    )],
    HealthCheckType="EC2",
    HealthCheckGracePeriod=300,
    Cooldown=300,
))
cacheASG = template.add_resource(autoscaling.AutoScalingGroup(
    "cacheASG",
    LaunchConfigurationName=Ref(lcCache),

    MinSize=Ref(cacheInstances),
    MaxSize="1",
    DesiredCapacity=Ref(cacheInstances),
    AvailabilityZones=[Select(0,(GetAZs(""))),Select(1,(GetAZs("")))],
    VPCZoneIdentifier=[Ref(PrimarySubnet),Ref(SecondarySubnet)],
    LoadBalancerNames=[Ref(cacheELB)],
     Tags=[autoscaling.Tag(
      "td:type" ,"TxCache", True
    )],
    HealthCheckType="EC2",
    HealthCheckGracePeriod=300,
    Cooldown=300,
))
cw=str(uuid4().int)
cacheWaitCondition = template.add_resource(cloudFormation.WaitCondition(
    cw,
    Count=len(config.CachePorts),
    Handle = Ref(cacheWaitHandle),
    Timeout = config.cacheTimeout,

))
txASG = template.add_resource(autoscaling.AutoScalingGroup(
    "txASG",
    LaunchConfigurationName=Ref(lcTxHttp),
    DependsOn=cw,
    MinSize=Ref(cpuMinInstances),
    MaxSize=Ref(cpuMaxInstances),
    DesiredCapacity=Ref(cpuDesiredInstances),
    AvailabilityZones=[Select(0,(GetAZs(""))),Select(1,(GetAZs("")))],
    VPCZoneIdentifier=[Ref(PrimarySubnet),Ref(SecondarySubnet)],
    LoadBalancerNames=[Ref(txELB),Ref(txELBPvn),Ref(txELBTbs),Ref(txELBTbl)],
    Tags=[autoscaling.Tag(
      "td:type" ,"TxHttp", True
    )],
    HealthCheckGracePeriod=900,
    HealthCheckType="ELB",
    Cooldown=300,

))
txASGTime = template.add_resource(autoscaling.AutoScalingGroup(
    "txASGTime",
    LaunchConfigurationName=Ref(lcTxHttp),
        HealthCheckGracePeriod=900,
    HealthCheckType="ELB",
    DependsOn=cw,
    MinSize=Ref(timeInstancesLow),
    MaxSize=Ref(timeInstancesHigh),
    DesiredCapacity=Ref(timeInstancesLow),
    AvailabilityZones=[Select(0,(GetAZs(""))),Select(1,(GetAZs("")))],
    VPCZoneIdentifier=[Ref(PrimarySubnet),Ref(SecondarySubnet)],
    LoadBalancerNames=[Ref(txELB),Ref(txELBPvn),Ref(txELBTbs),Ref(txELBTbl)],
    Tags=[autoscaling.Tag(
      "td:type" ,"TxHttp", True
    )],


    Cooldown=300,

))


# Creating Scaling Policy A
upscalingpolicyLoad = template.add_resource(autoscaling.ScalingPolicy(
    "upscalingpolicyLoad",
    AdjustmentType="ChangeInCapacity",
    AutoScalingGroupName=Ref(txASG),
    Cooldown="300",
    ScalingAdjustment="1",
))
# Creating Scaling Policy A
downscalingpolicyLoad = template.add_resource(autoscaling.ScalingPolicy(
    "downscalingpolicyLoad",
    AdjustmentType="ChangeInCapacity",
    AutoScalingGroupName=Ref(txASG),
    Cooldown="300",
    ScalingAdjustment="-1",
))
# Creating CloudWatch Alarm A
cpualarmhighTx = template.add_resource(cloudwatch.Alarm(
    "cpualarmhighTx",
    EvaluationPeriods=config.EvaluationPeriods,
    Statistic="Average",
    Threshold=config.ScaleUpCpu,
    Period=config.Period,
    AlarmActions=[Ref(upscalingpolicyLoad)],
    MetricName="CPUUtilization",
    ComparisonOperator="GreaterThanThreshold",
    Namespace="AWS/EC2",
     Dimensions=[cloudwatch.MetricDimension(
      Name = "AutoScalingGroupName",
      Value = Ref(txASG)
    )]
))
# Creating CloudWatch Alarm A
cpualarmlowTx = template.add_resource(cloudwatch.Alarm(
    "cpualarmlowTx",
    EvaluationPeriods=config.EvaluationPeriods,
    Statistic="Average",
    Threshold=config.ScaleDownCpu,
    Period=config.Period,
    AlarmActions=[Ref(downscalingpolicyLoad)],
    MetricName="CPUUtilization",
    ComparisonOperator="LessThanThreshold",
    Namespace="AWS/EC2",
     Dimensions=[cloudwatch.MetricDimension(
      Name = "AutoScalingGroupName",
      Value = Ref(txASG)
    )]
))



scheduleScaleUp = template.add_resource(autoscaling.ScheduledAction(
    "scheduleScaleUp",
    AutoScalingGroupName=Ref(txASGTime),
    DesiredCapacity=Ref(timeInstancesHigh),
    Recurrence=FindInMap("RegionMap", Ref("AWS::Region"), "ScaleUpCron"),
    MinSize=Ref(timeInstancesHigh),
    MaxSize=Ref(timeInstancesHigh),
))
scheduleScaleDown = template.add_resource(autoscaling.ScheduledAction(
    "scheduleScaleDown",
    AutoScalingGroupName=Ref(txASGTime),
    DesiredCapacity=Ref(timeInstancesLow),
    Recurrence=FindInMap("RegionMap", Ref("AWS::Region"), "ScaleDownCron"),
    MinSize=Ref(timeInstancesLow),
    MaxSize=Ref(timeInstancesLow),

))
highCPUloadcache = template.add_resource(cloudwatch.Alarm(
  "highCPUloadcache",
  MetricName = "CPUUtilization",
  DependsOn=cw,
  Statistic="Average",
  Threshold="85",
  ComparisonOperator="GreaterThanThreshold",
  Period="60",
  EvaluationPeriods="30",
  Namespace="EC2",
  OKActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  InsufficientDataActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  AlarmActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  Dimensions=[
    cloudwatch.MetricDimension(
      Name= "AutoScalingGroupName",
      Value = Ref(cacheELB)
  )]
))

highCPUload = template.add_resource(cloudwatch.Alarm(
  "highCPUload",
  MetricName = "CPUUtilization",
  DependsOn=cw,
  Statistic="Average",
  Threshold="85",
  ComparisonOperator="GreaterThanThreshold",
  Period="60",
  EvaluationPeriods="30",
  Namespace="EC2",
  OKActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  InsufficientDataActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  AlarmActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  Dimensions=[
    cloudwatch.MetricDimension(
      Name= "AutoScalingGroupName",
      Value = Ref(txASG)
  )]
))

unhealthytx = template.add_resource(cloudwatch.Alarm(
  "unhealthytx",
  MetricName = "UnHealthyHostCount",
  DependsOn=cw,
  Statistic="Average",
  Threshold="1",
  ComparisonOperator="GreaterThanOrEqualToThreshold",
  Period="60",
  EvaluationPeriods="9",
  Namespace="ELB",
  OKActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  InsufficientDataActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  AlarmActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  Dimensions=[
    cloudwatch.MetricDimension(
      Name= "LoadBalancerName",
      Value = Ref(txELB)
  )]
))


latencySpace = template.add_resource(cloudwatch.Alarm(
  "latencySpace",
  MetricName = "Latency",
  DependsOn=cw,
  Statistic="Average",
  Threshold="0.05",
  ComparisonOperator="GreaterThanThreshold",
  Period="900",
  EvaluationPeriods="3",
  Namespace="ELB",
  OKActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  InsufficientDataActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  AlarmActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  Dimensions=[
    cloudwatch.MetricDimension(
      Name= "LoadBalancerName",
      Value = Ref(spaceELB)
  )]
))

lowtraffictbs = template.add_resource(cloudwatch.Alarm(
  "lowtraffictbs",
  MetricName = "RequestCount",
  DependsOn=cw,
  Statistic="Sum",
  Threshold="10",
  ComparisonOperator="LessThanOrEqualToThreshold",
  Period="300",
  EvaluationPeriods="5",
  Namespace="ELB",
  OKActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  InsufficientDataActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  AlarmActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  Dimensions=[
    cloudwatch.MetricDimension(
      Name= "LoadBalancerName",
      Value = Ref(txELBTbs)
  )]
))

lowtraffictbl = template.add_resource(cloudwatch.Alarm(
  "lowtraffictbl",
  MetricName = "RequestCount",
  DependsOn=cw,
  Statistic="Sum",
  Threshold="10",
  ComparisonOperator="LessThanOrEqualToThreshold",
  Period="300",
  EvaluationPeriods="5",
  Namespace="ELB",
  OKActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  InsufficientDataActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  AlarmActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  Dimensions=[
    cloudwatch.MetricDimension(
      Name= "LoadBalancerName",
      Value = Ref(txELBTbl)
  )]
))

unhealthyspace = template.add_resource(cloudwatch.Alarm(
  "unhealthyspace",
  MetricName = "UnHealthyHostCount",
  DependsOn=cw,
  Statistic="Average",
  Threshold="1",
  ComparisonOperator="GreaterThanOrEqualToThreshold",
  Period="60",
  EvaluationPeriods="5",
  Namespace="ELB",
  OKActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  InsufficientDataActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  AlarmActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  Dimensions=[
    cloudwatch.MetricDimension(
      Name= "LoadBalancerName",
      Value = Ref(spaceELB)
  )]
))

unhealthycache = template.add_resource(cloudwatch.Alarm(
  "unhealthycache",
  MetricName = "UnHealthyHostCount",
  DependsOn=cw,
  Statistic="Average",
  Threshold="1",
  ComparisonOperator="GreaterThanOrEqualToThreshold",
  Period="300",
  EvaluationPeriods="5",
  Namespace="ELB",
  OKActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  InsufficientDataActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  AlarmActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  Dimensions=[
    cloudwatch.MetricDimension(
      Name= "LoadBalancerName",
      Value = Ref(cacheELB)
  )]
))

lowtraffictx = template.add_resource(cloudwatch.Alarm(
  "lowtraffictx",
  MetricName = "RequestCount",
  DependsOn=cw,
  Statistic="Sum",
  Threshold="500",
  ComparisonOperator="LessThanOrEqualToThreshold",
  Period="300",
  EvaluationPeriods="3",
  Namespace="ELB",
  OKActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  InsufficientDataActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  AlarmActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  Dimensions=[
    cloudwatch.MetricDimension(
      Name= "LoadBalancerName",
      Value = Ref(txELB)
  )]
))

latencyCache = template.add_resource(cloudwatch.Alarm(
  "latencyCache",
  MetricName = "Latency",
  DependsOn=cw,
  Statistic="Average",
  Threshold="0.05",
  ComparisonOperator="GreaterThanThreshold",
  Period="900",
  EvaluationPeriods="3",
  Namespace="ELB",
  OKActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  InsufficientDataActions =[ FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  AlarmActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  Dimensions=[
    cloudwatch.MetricDimension(
      Name= "LoadBalancerName",
      Value = Ref(cacheELB)
  )]
))
# Latency alarm
latencyTx = template.add_resource(cloudwatch.Alarm(
  "latencyTx",
  MetricName = "Latency",
  DependsOn=cw,
  Statistic="Average",
  Threshold="0.05",
  ComparisonOperator="GreaterThanThreshold",
  Period="900",
  EvaluationPeriods="3",
  Namespace="ELB",
  OKActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  InsufficientDataActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  AlarmActions = [FindInMap("VpcMap",FindInMap("RegionMap",Ref("AWS::Region"),Ref(StackEnv)),'AlarmTopic')],
  Dimensions=[
    cloudwatch.MetricDimension(
      Name= "LoadBalancerName",
      Value = Ref(txELB)
  )]
))



#Applying tags
for o in template.resources:
	if hasattr(template.resources[o], 'Tags'):
		if type(template.resources[o]) is autoscaling.AutoScalingGroup:
			template.resources[o].Tags.append(autoscaling.Tag("Name",Ref("AWS::StackName"),True))
			template.resources[o].Tags.append(autoscaling.Tag("td:region",Ref("AWS::Region"),True))
			template.resources[o].Tags.append(autoscaling.Tag("td:env",Ref(StackEnv),True))
			template.resources[o].Tags.append(autoscaling.Tag("td:application","Hercules",True))
			template.resources[o].Tags.append(autoscaling.Tag("td:build",Ref(BuildNumber),True))
		else:
			t = Tags( Name=Ref("AWS::StackName"))
			t.tags.append({
			  "Key" : "td:region",
			  "Value" : Ref("AWS::Region")
			})
			t.tags.append({
			  "Key" : "td:env",
			  "Value" : Ref(StackEnv)
			})
			t.tags.append({
			  "Key" : "td:application",
			  "Value" : "Hercules"
			})
			t.tags.append({
			  "Key" : "td:build",
			  "Value" : Ref(BuildNumber)
			})
			template.resources[o].Tags = t
print(template.to_json(sort_keys=False))