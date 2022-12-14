#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.chaliceapp import ChaliceApp
from stacks.storage_infrastructure import Storage
from stacks.presentation_infrastructure import Presentation

app = cdk.App()
Presentation(app, 'presentation')
Storage(app, 'storage')
ChaliceApp(app, 'cdkdemo')


app.synth()
