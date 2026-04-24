#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.strengthwise_stack import StrengthwiseStack

app = cdk.App()
StrengthwiseStack(app, "StrengthwiseStack")
app.synth()
