import click
import boto3
import os
import time
import string
import ConfigParser

from getpass import getpass
from os.path import expanduser


@click.group()
def cli():
    pass


@cli.command(
    'get-token',
    help='Gets STS session token')
@click.option(
    '-r', '--region',
    help='AWS region')
@click.option(
    '-p', '--profile',
    default='default',
    help='AWS shared credentials profile')
@click.option(
    '-d', '--duration', default=3600,
    help='STS token TTL in seconds')
@click.option(
    '-o', '--output-profile',
    help='Shared credentials profile name to be written / overwritten')
def get_token(
    region,
    profile,
    duration,
    output_profile
):
    profile_name = profile
    all_profiles = get_configs()

    profile = all_profiles.get(profile_name)
    if profile is None:
        raise Exception('profile {} not found'.format(profile_name))


    params = {
        'DurationSeconds': duration,
    }
    if profile.mfa_serial is not None:
        params['SerialNumber'] = profile.mfa_serial
        params['TokenCode'] = getpass('MFA ({}): '.format(profile.mfa_serial))

    if profile.is_assume_role:
        session = boto3.Session(
            aws_access_key_id=profile.source_profile.aws_access_key_id,
            aws_secret_access_key=profile.source_profile.aws_secret_access_key,
            region_name=region)
        client = session.client('sts')

        params['RoleArn'] = profile.role_arn
        params['RoleSessionName'] = str(time.time())

        response = client.assume_role(**params)
    else:
        session = boto3.Session(
            aws_access_key_id=profile.aws_access_key_id,
            aws_secret_access_key=profile.aws_secret_access_key,
            region_name=region)
        client = session.client('sts')
        response = client.get_session_token(**params)


    if output_profile is None:
        output_profile = '_{}'.format(profile_name)

    aws_secret_access_key = response['Credentials']['SecretAccessKey']
    aws_access_key_id = response['Credentials']['AccessKeyId']
    aws_session_token = response['Credentials']['SessionToken']

    write_profile(output_profile,  {
        'aws_secret_access_key': aws_secret_access_key,
        'aws_access_key_id': aws_access_key_id,
        'aws_session_token': aws_session_token,
    })

    print response


def get_configs():
    configs = {}

    credential_parser = ConfigParser.ConfigParser()
    credential_parser.read(expanduser('~/.aws/credentials'))

    for section in credential_parser.sections():
        data = dict(credential_parser.items(section))
        configs[section] = Config(section, **data)

    config_parser = ConfigParser.ConfigParser()
    config_parser.read(expanduser('~/.aws/config'))

    for section in config_parser.sections():
        profile_name = section.split(' ')[1]
        data = dict(config_parser.items(section))
        if profile_name in configs:
            configs[profile_name].data.update(data)
        else:
            configs[profile_name] = Config(profile_name, **data)

        if configs[profile_name].source_profile:
            configs[profile_name].source_profile = configs[configs[profile_name].source_profile]

    return configs


def write_profile(profile, values):
    configure_frm = 'aws configure --profile {aws_profile} set {name} {value}'

    for name, value in values.iteritems():
        os.system(configure_frm.format(
            aws_profile=profile,
            name=name,
            value=value,
        ))

    print 'Saved credentials profile "{}"!'.format(profile)


class Config(object):
    def __init__(self, name, **kwargs):
        self.name = name
        self.data = kwargs

    @property
    def is_assume_role(self):
        return self.role_arn

    def __getattr__(self, name):
        return self.data.get(name)


if __name__ == '__main__':
    cli()
