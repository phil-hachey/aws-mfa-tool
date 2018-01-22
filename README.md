# AWS MFA tool

This is a simple CLI tool to write temporary credentials to `~/.aws.credentials` so they could be used as normal credentials. This need arose as a work around to Terraform's lack of MFA support when assuming roles (https://github.com/terraform-providers/terraform-provider-aws/issues/2420).

## Installation

```
pip install aws-mfa-tool
```

## Usage

```
> aws-mfa --profile example_profile --mfa-serial <mfa_serial>
```

This will prompt your for your MFA token. On successful entry, it will print and save the temporary credentials to you `~/.aws/credentials` file. The saved profile name is _< profile_name > by default, so `_example_profile` in this example.

With this, you can set the `AWS_PROFILE` env var
```
export AWS_PROFILE=_example_profile
terraform cmd
```

Since the "aws:MultiFactorAuthPresent" condition is already met with these temporary credentials, you're free to use `assume_role` block with the aws provider in terraform.

```
provider "aws" {
  alias  = "dev_account"
  region = "${var.aws_region}"

  assume_role {
    role_arn = "${var.dev_account_target_role_arn}"
  }
}
```

### aws-mfa create --help

```
Usage: aws-mfa create [OPTIONS]

  Gets STS session token

Options:
  -r, --region TEXT               AWS region
  -p, --profile TEXT              AWS shared credentials profile
  -m, --mfa-serial TEXT           MFA serial ARN
  -t, --token-code TEXT           MFA token code. If this is ommitted and
                                  --mfa-serial is given, you will be prompted
                                  for a code
  -d, --duration INTEGER          STS token TTL in seconds
  -o, --save-output-profile TEXT  Shared credentials profile name to be
                                  written / overwritten
  -s, --skip-save                 Skip save to shared credentials
  --help                          Show this message and exit.
```

Note I haven't tested out all the options yet, just the happy path. Feel free to submit a PR :)
