#Region	Region Name	Elastic Load Balancing Account ID
#us-east-1	US East (N.Virginia)	127311923021
#us-west-1	US West (N.California)	027434742980
#us-west-2	US West (Oregon)	797873946194
#eu-west-1	EU (Ireland)	156460612806
#ap-northeast-1	Asia Pacific (Tokyo)	582318560864
#ap-southeast-1	Asia Pacific (Singapore)	114774131450
#ap-southeast-2	Asia Pacific (Sydney)	783225319266
#sa-east-1	South America (Sao Paulo)	507241528517
#cn-north-1	China (Beijing)	638102146993
#us-gov-west-1 	AWS GovCloud (US) 	048591011584

#TODO kolla health checks, satt upp overvakning for nordcloud


# TXHttpType should be fine using  m3.xlarge.  The minimum ram needed is 10 GB
# m3.xlarge has half the CPU power but cost 40% less
ZoneMap = {
  "ACC" : {
    "pvn" : "Z2BWVURQU57IG1",
    "pvnName" : "gtuat.tdtest.net",
    "td" : "Z2BWVURQU57IG1",
    "tdName": "gtuat.tdtest.net"
  },
  "PROD" : {
    "pvn" : "Z1MSN2UI59M404",
    "pvnName" : "pvnsolutions.com",
    "td" : "Z3NBKMGXOG8T5K",
    "tdName" : "tradedoubler.com",

  }

}

RegionMap = {
    "us-east-1": {
      "AMI": "ami-76817c1e",
      "ACC" : "vpc-3409a751",
      "PROD" : "vpc-2c09a749",
      "ELBAccount" : "127311923021",
      "ScaleUpCron" : "0 1 * * *",
      "ScaleDownCron" : "59 17 * * *",
      "TXSpaceType": "m3.large",
      "TXHttpType" : "m3.xlarge",
      "TXCacheType" : "r3.xlarge",

    },

    "ap-southeast-1" : {
        "AMI" : "ami-ac5c7afe",
        "PROD" : "vpc-782bdd1d",
        "ELBAccount": "114774131450",
        "ScaleUpCron" : "0 1 * * *",
        "ScaleDownCron" : "0 18 * * *",
        "TXSpaceType": "m3.large",
        "TXHttpType" : "m3.xlarge",
        "TXCacheType" : "r3.xlarge",

   },
    "us-west-1": {
      "AMI": "ami-f0d3d4b5"
    },
    "us-west-2": {
        "AMI": "ami-d13845e1",
        "PROD" : "vpc-bfd73dda",
        "ACC" : "vpc-dc806bb9",
        "ELBAccount" : "797873946194",
        "ScaleUpCron" : "0 1 * * *",
        "ScaleDownCron" : "59 17 * * *",
        "TXSpaceType": "m3.large",
        "TXHttpType" : "m3.xlarge",
        "TXCacheType" : "r3.xlarge",

    },
    "eu-west-1": {
      "AMI": "ami-892fe1fe",
      "PROD" : "vpc-140ce671",
      "ELBAccount" : "156460612806",
      "ScaleUpCron" : "0 7 * * *",
      "ScaleDownCron" : "59 23 * * *",
      "TXSpaceType": "m3.large",
      "TXHttpType" : "m3.xlarge",
      "TXCacheType" : "r3.xlarge",

    },
    "sa-east-1": {
      "AMI": "ami-c9e649d4"
    },

    "ap-northeast-1":
    {
        "AMI": "ami-29dc9228"
    }
}
cacheTimeout=3600
VpcMap = {
#ACC_us-east-1
    "vpc-3409a751" : {
      "SubnetPrimary" :"172.31.144.0/24",
      "SubnetSecondary" :"172.31.145.0/24",
      "VGW" : "vgw-a0a042c9",
      "CGW": "cgw-c66784af",
      "IGW" : "igw-197eb37c",
      "VPNroutes" : [
          "10.240.0.0/17",
          "172.22.10.0/24",
          "172.22.12.0/24",
      ],
      "Network" : "172.31.144.0/21",
      "AlarmTopic": "arn:aws:sns:us-east-1:644602157532:techdev",
    },

#PROD_us-east-1
    "vpc-2c09a749" : {
      "SubnetPrimary" :"172.31.208.0/24",
      "SubnetSecondary" :"172.31.209.1/24",
      "VGW" : "vgw-a1a042c8",
      "CGW" : "cgw-c66784af",
      "IGW" : "igw-1b7eb37e",
      "VPNroutes" : [
        "10.240.128.0/17",
         "172.22.11.0/24",
         "172.22.12.0/24",
      ],
      "Network" : "172.31.208.0/21",
      "AlarmTopic": "arn:aws:sns:us-east-1:644602157532:pagerduty",
    },
#PROD_eu-west-1
    "vpc-140ce671" : {
      "SubnetPrimary" : "172.31.201.0/24",
      "SubnetSecondary" : "172.31.202.0/24",
      "VGW" : "vgw-028bbc76",
      "CGW" : "cgw-4945733d",
      "IGW" : "igw-4883662d",
      "VPNroutes" : [
          "10.240.128.0/17",
          "172.22.11.0/24",
          "172.22.12.0/24",
            #172.31.192.0/21 Was added to the vpn but i think it should not be there
      ],
     "Network": "172.31.200.0/21",
     "AlarmTopic": "arn:aws:sns:eu-west-1:644602157532:nordcloud-pagerduty",
    },
#PROD_us-west-2
    "vpc-bfd73dda" : {
       "SubnetPrimary" : "172.31.193.0/24",
      "SubnetSecondary" : "172.31.194.0/24",
      "VGW" : "vgw-c421fcda",
      "CGW" : "cgw-3075a82e ",
      "IGW" : "igw-6346a606",
      "VPNroutes" : [
          "10.240.128.0/17",
          "172.22.11.0/24",
          "172.22.12.0/24",
            #172.31.200.0/21 Was added to the vpn but i think it should not be there
      ],
     "Network": "172.31.192.0/21",
     "AlarmTopic": "arn:aws:sns:us-west-2:644602157532:pagerduty-nordcloud",

    },
#PROD_ap-southeast-1
   "vpc-782bdd1d" : {
      "SubnetPrimary" : "172.31.224.0/24",
      "SubnetSecondary" : "172.31.225.0/24",
      "IGW": "igw-0d3fdc68",
      "CGW": "cgw-eef289bc",
      "VGW" : "vgw-5f770c0d",
      "VPNroutes" : [
      "10.240.128.0/17",
         "172.22.11.0/24",
         "172.22.12.0/24",
      ],
      "Network" : "172.31.224.0/22",
      "AlarmTopic": "arn:aws:sns:ap-southeast-1:644602157532:pagerduty-nordcloud",

   },
#ACC_us-west-2
    "vpc-dc806bb9" : {
       "SubnetPrimary" : "172.31.128.0/24",
      "SubnetSecondary" : "172.31.129.0/24",
      "VGW" : "vgw-e42af7fa",
      "CGW" : "cgw-4024f95e",
      "IGW" : "igw-827f9ee7",
      "VPNroutes" : [
          "10.240.0.0/17",
          "172.22.10.0/24",
          "172.22.12.0/24",
            #172.31.192.0/21 Was added to the vpn but i think it should not be there
      ],
     "Network": "172.31.128.0/21",
     "AlarmTopic": "arn:aws:sns:us-west-2:644602157532:techdev",
    }
}

Certificates = {
# OLD  "elb-star_pvnsolutions.com" : "arn:aws:iam::644602157532:server-certificate/ELB-star.pvnsolution.com",
  "elb-star_pvnsolutions.com" : "arn:aws:iam::644602157532:server-certificate/new-elb-star.pvnsolution.com",
  "elb-tbl_tradedoubler.com" : "arn:aws:iam::644602157532:server-certificate/elb-tbl_tradedoubler.com",
  "elb-tbs_tradedoubler.com" : "arn:aws:iam::644602157532:server-certificate/elb-tbs_tradedoubler.com",
  "startTD_1" : "arn:aws:iam::644602157532:server-certificate/ELB-star.tradedoubler.com-2"
}

CachePorts ={
  "AdGroupConnectionCache":4711,
  "AdGroupGECache":4712,
  "AdNetProgramCache":4713,
  "Admin":4714,
  "AffiliateCache":4716,
  "BLCache":4717,
  "BudgetCache":4718,
  "CallCache":4719,
  "CampaignCache":4720,
  "ContainerTagCache":4721,
  "CountryIPCache":4722,
  "EventCache":4723,
  "FileCache":4724,
  "GECache":4725,
  "GeoCache":4726,
  "IPTargetingCache":4727,
  "LocationCache":4728,
  "MiscCache":4729,
  "OrganizationCache":4730,
  "PACache":4731,
  "PALCache":4764,
  "PHCache":4732,
  "PoolCache":4733,
  "ProgramCache":4734,
  "RetargetingCache":4736,
  "TestsCache":4737,
  "UserAgentTargetingCache":4738,
  "VoucherCache":4761,
  "SiteCache":4762,
  "AdNetService":4741,
#  "KeywordCache": 4742
}

SshKeys = {

#evry's pubkey  "evry" : "",
  "Ani" : "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCwhZlGQh9GC/ZkeqwGG0grvRsBAZMlxYDrf1rY8Z4iAPtRrstbQbnxL3Cc+rUbRmfcwEqEsqSgHiON1kSZ/NmSbZyGs8eGZ3Og/CfcbhUTVAUJwPGerLXeTNwUcW4SI6K8E8+3o3F1XyCLqPPw3smm1k6cwO/qIf93xviRkJ2VeGAGrcG3m3ERBona36LOywQcKp/WLgGft7dwF4fYKQkV5lCe57BIRXlnZ+i7g7H4q1HusJ75Ys+PFPpGbsFJiZ/dqe7iErP88o0YWIkcBq3x77oqiLz1c74nQafiJRi97YvUZXYQsf5ZgEtM76691yxECKa8tLLg208a3bwMaxrjk5NdMmXleBh0plbwfophikyOmr09mnIBNzEH9uWRPZn9McbYn0NvebccFu/AFkryIOmuncBNaHKL8si/I/ZKeEwlGStAkAbSCi6fd7xMAX7YAktt1FnBTKNCd8klR5sruE11158xgpmEaIVFdRYTOEaaG4kelQPqyE3pxsk9ykK8Uh+tySQjlDKgI2zNF2bFUu5XO0kArbcgv5CbB7jlypt4QTV8Z2Os+E0k3uHyWfJHACa6ESMBNc/5n09tGLjYkffJSpiYmGCqfAnzcbdHKiqjUyqv6kGeWki+YEUPOY4kbLHqLZEkY4OikAMRxWoLZ/4ATMfR3WySY7SOzuVn1w== phpseclib-generated-key",
  "ludwigilmander" : "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC8MGDNPT2d5RHF4eXbw7zYrknBMUt9JJkjLLgWybzLS7DfrHmo0+UlCQrdQiwcvRBIHPWa2t6O1blJAx5930NnnCiwiMn1nH+UrF/1ZFWElc9KQgsjVmZczq5sWphdQiUEgZ7fF77T+XtsC9Z9hP5YeL+8MHfHS5IUkpR/IHTez1qA4X4cxDhs+OPEiu7sWQ7N732EIYax0bfxgh6+SSkSStf3ehBo+m5lMvPYHLsFAsEcZ+Koc78qIwb7GqAgRxx8mkLnEm5/yJLIlUa8tAu4XJN7qHkfc+kqWV2XA5KU4KGBS6VaQD9fc4HfyDnpNeFjVSK8+Rx5rYZyGiE4fYXh ludwig.ilmander@nordcloud.se",
  "martin" : "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC3j8yMKRpL4Y5QwQeM94/1Rzav2dRRbEzyns1OMmG4l75KupqDb2vHWOnXy6he0Fc497BrKT0L00ZT7INQq7+bgClNMvZefN6UZgM9gVcWkz1nmCzhu1/WeieeHjFsplUAjH86npN59sk1RQEY8O8ZcIWHi7AIadN1Sx5rQWT41eO00Lb0bNIk0jPDJN5JmbA3R4zWisuf0D9D+68zkP7UNL4qJyD27+LSOiv6Y7RbdQ62H7MZvq2tC519+IMTsCDJCuGhrbumKvAv74VAi66fmnQKPZQzl+l++OLU9vz6SMKpttKHynxdW2Si7bJZ4UwEAburBP5uy+su6YaJt80Iav3Uyj0CGExU8s+9TNIrcXrTnKuaxO+bTlXRAmVVf0l0rKlmoDb4s++xba3WVFEYThO7MysgDcCte8Trg1mXNrYerWSZt3RLlqLYE+S9Clh6yBfHLDdKGWh1U5TLY6Elj++d3K5LRb4XDFevEEdWigcsEa8Uxwi9i+6DlMRUijk9wQeegrWOozEmvcJLBXQY+svIEElYqUeYkDQRpJQgHo9h75o7ewAOhId+QA+X2n/ItwZSto55IXj2gHMNDS5adzRzJLt3RZAp7oE2/yj3oqpLlJjZ152SKBEUulZ9uwKKnvxrwawc0AOMcRSnTIlduvTb90O6wJxzRpiKepGvTQ== fishdaemon",
  "MarkoHelenius" : "ssh-dss AAAAB3NzaC1kc3MAAACBAKAkphfl+Zi+0IlFXXLL9IDFBMvIVQmgwQVwt2J8KXHOtEKLBAPxHSgk3m06e+YR+xrfVt1npcELu5eV2cxkbCHQK55foORqPfNohJKffltQP9Echb4arcHLrQPQDbTVgpY+1Gb/HWmW2YYrItxMXT5Qp7w0XFxSMPm8j1BG2vnZAAAAFQD3qrzl8VKNPlGjmkiyFxQq87tcWQAAAIBmYkiFvRfVKM+NUjEVtBtdyFEqrrfBovekPpk5Y1iigBxJPMIo91lSOO6lKl5iG7jDdeMGrNWxic2GvLPffuqzvq77SoK7UcxhNLfBZnSqTa2Cz+x9r4KWKrIO8mz0akaMtd5QKA4UGUmjsUCDjZqbW1Ho88Ql1ADM8odXsU7y9AAAAIEAjL7TM+isS0cQGHhDmDJn00D53yyncGYkUAq9kQWSoveAZ2bRgvvXp3EHtflqpb949yXeluorb6PDPt+r92ZN37JWfebod9nwzk9HWT//0XEIf5xzAQ9CK5QAt8z7C0THvN1661FN/WdSF8UlPrJRb6J4yFxDBQYHWjnajZR5dZo= ahma@bigsur",
  "AnttiMalmia1" : "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDEiitcymxBkThiEs3IU/EpcsEo/p9wVAJnE7O/fvQ8OsM7ajrb2Gm7K6mLygxDVkC17X9hfJhAbNVALKKPVAMEjhA6op38a/Sp8NfoJSSgv4/aQ/qHEiuY177nR5S13+pFQ7MdWEe7ak8nBK1Et62S3LGeTPg5/zM9jM75OTfSwaJl9wjBLhdhcfdxhiGDWC8PB8vPjAHcHW2k4YWHtb8Aqv27hvXd5iTeOPOoICXWnckwNOXiObdHXERlz9NlhDFN103aHP2ok9oRy9MqnLY4nn72OplAJTvBPikH28LUNQudna7FFKuLtFrzjxmgalOzOQN4t6EUQGeekwfWkfMT cyrus@coffee",
  "AnttiMalmia2" : "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCd8fok98APKGF4k2+5N8s/kLUsNhxPwFm4s4BMOBPsNJCCOEOHNit3lLmoSnsz1bYJkSA3xESJkPJspL03fE4Z6m7r7+4sFJI5RA7BZng8fJ7fei80jfgLi7gXP1YVuU6Nup1R6Cpsf/UakVnQY25x4y67KNroPvLXX3SkYX3Vu4s0BIaJuRavv9DxMKE/q57PkhMLrJqk3s7CoyBmoI54Intnj9Hxqu/oHMwpDL4hN7py2XzY+d6jUzap53QEETc82eODQQk/oOdeGsTzoTB0AxjkRlG4EzOY6oBZ0GYm2QV/+Al4SRiLOgcv9VlkeBPRVYsDFmWlvwvDyTtoT7lt cyrus@Lemppu",
  "PetriKallberg" : "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAuZ1XISfOseuEufdDsvoiaj7C78d5SsuKiYh/Ya+iKTUvHshoi6dD5cIKiIVJ9lGbWhWDKIeGTbWvkyX4aZphEvxyiFHYQ4QuK4r6ejOeVg/bkIiRbPEg/eL2W3fJoQaiTOWASuOVv2glWSaHyc1Ez0olHsLkdEIIqPkZO85fooS3GzNeUFeeZuxXM4NwdMF/dNyE1my/wZO4VDqQOFnE33t2lBzIbENBht01TH+SPsABVXX3/6JPG7ByEVvFXpQtlO9wTlGB7SScEVKRu4F50OWYE56kadUS/EW7ez+2wG+ap4fdQrB4kUUU2r5GtbuDsN3WmEZmhESNNToLHfOizQ== kallu@Mac-mini.local",
  "LariPulkkinen" : "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC6fh+nx92LzNlEXeD+SKNFxo9sVSBa56/F9iRsM1sjArHXbBv1ay8KoR0QYtZNoTg8Yl9QHMwkNpj0bFk4F2y6+U95SLcP49bAotwdY/9nZEjNaP1ikenam8nFbu6+TNYcnSKsaJ8si78MeWdkNXw3oTyaQcu8EmMuzVB+SWn4OKJ3T7ve6P1fBzSzfzCXaIw8Cukk14RJPmniFZ8N05kislRnZh35x02Cmt43/uNOWT5BOp5DHN55lLHxn9IvquCzUwkyaIWBeTJxpyoYsij3cq0tZePslwO/lmNyoL54K2IdqzE+Wm5+xkr0bXQDfGdiwg90/8l6kJPhxLTh3LZN lari@Laris-MacBook-Air.local",
  "LariPulkkinen2" : "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC12KhyRS3BBfRSZYAILRHiUnCtgsNjUwhhJbv5T9OIaBEmsRCWLOuXSwAovGZPIjPEWtVYQju9Le5Ceaxzh8dDaWODPjsoSp9ovkjIUX60IVN7ob2yx4RpNPm+3P00enR1zCyCMQWYNwT43uZDI08mYEh3/E23mnA9+4NvRYQZ5E4PuRr5zkUais3nGwBy8Ay4pql1lGGZZGZG/8LXP1Nj9ovgpydUSHfFfWRVyVj03Xyu4kWxqVXJPUnD821FDESCJ7MgPqrX8sPuFpZM0Oz7Qd41DAG/Zc3JxzkhNOTmrGX8bo3qIzaL0PgdfaCvDeV3EkGy652W9H6GgaAHYXdJ lari.pulkkinen@nordcloud.fi",
  "MikkoKallio" : "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCXuarAHVIQz97Fc7o9ertYLfx5vG9VE5W6epORrM4zEup61Ksvs44iUijrlAFTor2ld/baf548kBcPGHlrp1k+tIsFHCU4N92fbG/wZDxWhARZ6Nbd/bHFSIfgbev3xewoBNKclmPaw9YyYl/uuNw1g4rTRNpZQAMbqT8bOd/ifeuzfSm8ISdJJF2sX71UlMJ+oFH2y/PIIbm1mJHJ78q4rhHakyRT1Xl2QQNA7I86Af+/F1wzD3cZECzsLKBULtVyp3dDOYzx/9EpwaZN8rieddnEZF+dOBGDX5ZH8tVSsvu0aEzlLyel/fqBOoPHspkKBNhWqTR9iVREz2jlJ3Uz miki@HP-ProBook-4320s",
  "MikkoKallio2" : "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC1mV1b+AYb1GvDztI/+43rQQePAs73vuf7V+4Iy5GPpsftqte0B+thnpH7M4qsBojtpMZksbJpl0WgOBusaMBtQdrQIw8gbsU8m3fmJNpxZ+01Cj5xofJwPuLgPa06TUc5o9FDS1TOmgl1R6vsI+bwExmxWYKeODOaQioGVjZ2px9+Yk4jkQ6zzN20oAljPQdohf7f+CFXDm9BItd6B15+VpTaVCHTw+FSbm8Slum/qlU4up9QRwa+CDSKjr77mu31P943O/XPy8+YBkjWzgfILTNbvQlIjL9SxYy9IBUXNpRJPWmfMnO+uTSE5hTZas/OU8c8Gyrn1adbxUrHzetF miki@aws",
  "TuomasToikkanen": "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAIBiHeUXOxfvWPXkxgTICmypYiiRpH6JjMkgsNbmidlyAqyW6v93TZ+R7rAfdsrAuxMn/Wju1B3afAE+OrEoio6IdTrF7wAoFn8QY+JGRkF9IiuUTWUNNGUeghNTrhf0h60Til9HCKRi6ObvV7iqL/QmDMjAOUql2YwiYB6xHUabfw== tuomas",
  "TuomasToikkanen2": "ssh-dss AAAAB3NzaC1kc3MAAACBALxY786r827nRlS7CFxODz8QdZFp8N6tEFVqQgpnMV8qVwDsS9X5R/KEihyp6M9fqHhlhHbimrXHVZ24Rnx2V1gbpkZY6K4QUU14RdLa1fuex/NlJH8S1OKRn/awtQ6u1KPWh8J45PViD8QtgkOP7tWeHFW6ZauVqx/X868b/V+BAAAAFQDgJRmu1p1maf6hNYZ6lZlBPHNLxQAAAIAzSUf9XA+ca0UuqFYVJk+X5GY5+OCY+4ilBqVM6DwnZFv7MQPDFG+1eM/f774H/V4RXwuFCH8+KnwI0rq1XF1hbRDFKsz6u7mnW8TpGHL7yIdLJ3ekC172TObuLb6Og5ux5op9yhbPzLmsw50iN+Diggc5/yGFwtuvn2vv38pNqQAAAIAA/KwLHU0Mq8nzPVZLFdZA2b+YRPd6eUqVAp3Ii7Rwhd/XBry8a5ZGbL7QHxLvfdTdUNYvEyDqQBXYcq7LJCeImD4yRKGPeERvo8xxv7yM+GFmeq84IW+MbFHJW4AbUTCtbNzGEFqyCpIdpo8aLkxcTFcJuI/kis9OmE2hi561Zw== tuomas@ubuntu",
  "TuomasToikkanen3": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDOCxsuA0OWsh43gSVEeyhQece7W0zOleN72q/ZdNRkpZZ46q24qoyROL9yzd6fzpfJlvcrp70NiOaG+9ABrNj8WCEE4OzPOJMyciVr8NslNNLfOvNFwCqn2ysbbnO/JbjGaJlKecbNqb0VrO+EpwypeUSCmRzaV4Cwuz/g257BxnSx7q2gJCParLx04N445r1F8I+yUpnCSDBPunK+hFahtjljGqJ4l+REE/KFX8JwXZz7ZKEnLPkrEaYluTuy8G7mHvCGAyiOIt/FH08mO3raVjo+J9B89Pt8uI5hJq1jWEpcWgWMqR839kTIq9bntF9aduNDD0xO3/EC3npa5B1f tuomas@ubuntu",
  "TuroLampinen" : "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAr+HJHVwmNJmJDYpopDNgJ5In3iFi0NjCeyPij0Ui7C9iZm/unwo0KNFmJNlztnqF2QGR3i9vQlRUoxmV6BwYFqQpQAsFRyJDtA4F3Dbr7Zv3TbuE6zltZV+hKMvCyd4cH/qyj2MDaAsnUTMTcxWiLU9vxmQWbDBA2ESZqXzIA9CRb5WWrPZGd02rUFzdGSP7ofckp29PNl6K50l5e0KUWMdoEjMkbXp8fJ85tM0kOFAjVRfadZ5RQg4DQz3HZ903IfweZB2mUPBO3uE4dRfqF7hGULXwFh9koZjUzDlS9wMi3A3BqaoPhYsfK3J3uhQtWelDWICTZJC2MmlW6L1Ubw== turo"
}

#CPU load threshhold in %
ScaleUpCpu="50"
ScaleDownCpu="30"


#Scaling periods
EvaluationPeriods="5"
Period="60"

