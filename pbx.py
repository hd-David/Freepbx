import boto3

sess=boto3.session.Session()
res=sess.resource('ec2')

#-------------------Create-VPC---------------------------

vpc=res.create_vpc(CidrBlock='10.0.0.0/16')
vpc.create_tags(Tags=[
        {
            'Key': 'Name',
            'Value': 'freepbx'
        },
    ])
vpc.wait_until_available()


#-------------------InternetGatewayId-----------------------

ig=res.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=ig.id)


#---------------------RouteTable------------------------------

route_table=vpc.create_route_table()
route_table.create_route(DestinationCidrBlock="0.0.0.0/0",
                         GatewayId=ig.id)

#--------------------Create-Subnets---------------------------

subnet=res.create_subnet(CidrBlock="10.0.0.0/24",VpcId=vpc.id)                                    
route_table.associate_with_subnet(SubnetId=subnet.id)

#------------------Create-SecurityGroup---------------------------

sec_group=res.create_security_group(GroupName="freepbx",
                                    Description="testing purpose",VpcId=vpc.id)
                        
sec_group.authorize_ingress(CidrIp='0.0.0.0/0',IpProtocol ='-1')

#--------------------Create-Ec2-Instance---------------------------

ec2 = boto3.resource('ec2')

# create a file to store the key locally
outfile = open('frepbx-key.pem','w')

# call the boto ec2 function to create a key pair
key_pair = ec2.create_key_pair(KeyName='frepbx-key')

# capture the key and store it in a file

KeyPairOut = str(key_pair.key_material)
outfile.write(KeyPairOut)
print("Key Pair hacker-key.pem successfully created")

inst=res.create_instances(ImageId='ami-0d9cca6f9ad40eb08',InstanceType='t3.small',
                          KeyName='frepbx-key',MaxCount=1,MinCount=1,
                          NetworkInterfaces=[{'SubnetId':subnet.id,'DeviceIndex':0,
                                              'AssociatePublicIpAddress': True,
                                              'Groups':[sec_group.group_id]}])

inst[0].wait_until_running()
print(inst[0])
print("EC2 instance successfully created with using VPC, Subnets, InternetGateway, SecurityGroup ")
#----------------------Complete-----------------------------