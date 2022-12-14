import aws_cdk as cdk
from aws_cdk import (
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins
)


class Presentation(cdk.Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Define a S3 bucket that contains a static website
        self.s3_bucket = self._create_hosting_s3_bucket()

        # Creates Cloudfront Origin Access Identity to access a restricted S3
        origin_access_identity = cloudfront.OriginAccessIdentity(
            self,
            'cdkTestOriginAccessIdentity'
        )

        # Allows Origin Access Control to read from S3
        self.s3_bucket.grant_read(origin_access_identity)

        # Define Cloudfront CDN that delivers from S3 bucket
        self.cdn = self._create_cdn(access_identity=origin_access_identity)

    def _create_hosting_s3_bucket(self):
        """ Returns a S3 instance that serves a static website """
        website_bucket = s3.Bucket(
            self,
            'static-website-for-cdkdemo',
            removal_policy=cdk.RemovalPolicy.DESTROY,
            access_control=s3.BucketAccessControl.PRIVATE,
        )

        # Populates bucket with files from local file system
        s3deploy.BucketDeployment(
            self,
            'DeployWebsite',
            destination_bucket=website_bucket,
            sources=[
                s3deploy.Source.asset('../frontend')
            ],
            retain_on_delete=False,
        )
        return website_bucket

    def _create_cdn(self, access_identity):
        """ Returns a CDN that delivers from a S3 bucket """
        return cloudfront.Distribution(
            self,
            'myDist',
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    self.s3_bucket,
                    origin_access_identity=access_identity,
                )
            )
        )

