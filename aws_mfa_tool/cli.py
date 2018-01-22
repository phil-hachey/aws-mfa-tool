import click
import boto3
import os
import random
import string

from getpass import getpass


@click.group()
def cli():
    pass


@cli.command(
    'create',
    help='Gets STS session token')
@click.option(
    '-r', '--region',
    help='AWS region')
@click.option(
    '-p', '--profile',
    help='AWS shared credentials profile')
@click.option(
    '-m', '--mfa-serial',
    help='MFA serial ARN')
@click.option(
    '-t', '--token-code',
    help='MFA token code. If this is ommitted and --mfa-serial is given, '
         'you will be prompted for a code')
@click.option(
    '-d', '--duration', default=86400,
    help='STS token TTL in seconds')
@click.option(
    '-o', '--save-output-profile',
    help='Shared credentials profile name to be written / overwritten')
@click.option(
    '-s', '--skip-save', is_flag=True,
    help='Skip save to shared credentials')
def create(
    region,
    profile,
    mfa_serial,
    duration,
    token_code,
    skip_save,
    save_output_profile
):
    session = boto3.Session(
        profile_name=profile,
        region_name=region)
    client = session.client('sts')

    params = {}

    if mfa_serial is not None:
        params['SerialNumber'] = mfa_serial

    if duration is not None:
        params['DurationSeconds'] = duration

    if token_code is not None:
        params['TokenCode'] = token_code
    elif mfa_serial is not None:
        params['TokenCode'] = getpass('Input MFA code: ')

    response = client.get_session_token(**params)

    if not skip_save:
        if save_output_profile is None:
            save_output_profile = '_{}'.format(profile)

        aws_secret_access_key = response['Credentials']['SecretAccessKey']
        aws_access_key_id = response['Credentials']['AccessKeyId']
        aws_session_token = response['Credentials']['SessionToken']

        write_profile(save_output_profile,  {
            'aws_secret_access_key': aws_secret_access_key,
            'aws_access_key_id': aws_access_key_id,
            'aws_session_token': aws_session_token,
        })

    print response


@cli.command(
    'assume-role',
    help='STS assume role')
@click.option(
    '-r', '--region',
    help='AWS region')
@click.option(
    '-p', '--profile',
    default='default',
    help='AWS shared credentials profile')
@click.option(
    '-r', '--role-arn',
    required=True,
    help='AWS shared credentials profile')
@click.option(
    '--role-session-name',
    help='AWS shared credentials profile')
@click.option(
    '-m', '--mfa-serial',
    help='MFA serial ARN')
@click.option(
    '-t', '--token-code',
    help='MFA token code. If this is ommitted and --mfa-serial is given, '
         'you will be prompted for a code')
@click.option(
    '-d', '--duration',
    default=3600,
    help='STS token TTL in seconds')
@click.option(
    '-o', '--save-output-profile',
    help='Shared credentials profile name to be written / overwritten')
@click.option(
    '-s', '--skip-save',
    is_flag=True,
    help='Skip save to shared credentials')
def create(
    region,
    profile,
    role_arn,
    role_session_name,
    mfa_serial,
    duration,
    token_code,
    skip_save,
    save_output_profile
):
    session = boto3.Session(
        profile_name=profile,
        region_name=region)
    client = session.client('sts')

    params = {
        'RoleArn': role_arn
    }

    if mfa_serial is not None:
        params['SerialNumber'] = mfa_serial

    if duration is not None:
        params['DurationSeconds'] = duration

    if token_code is not None:
        params['TokenCode'] = token_code
    elif mfa_serial is not None:
        params['TokenCode'] = getpass('Input MFA code: ')

    if role_session_name is None:
        params['RoleSessionName'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
    else:
        params['RoleSessionName'] = role_session_name

    response = client.assume_role(**params)

    if not skip_save:
        if save_output_profile is None:
            save_output_profile = '_{}'.format(profile)

        aws_secret_access_key = response['Credentials']['SecretAccessKey']
        aws_access_key_id = response['Credentials']['AccessKeyId']
        aws_session_token = response['Credentials']['SessionToken']

        write_profile(save_output_profile,  {
            'aws_secret_access_key': aws_secret_access_key,
            'aws_access_key_id': aws_access_key_id,
            'aws_session_token': aws_session_token,
        })

    print response


def write_profile(profile, values):
    configure_frm = 'aws configure --profile {aws_profile} set {name} {value}'

    for name, value in values.iteritems():
        os.system(configure_frm.format(
            aws_profile=profile,
            name=name,
            value=value,
        ))

    print 'Saved credentials profile "{}"!'.format(profile)


if __name__ == '__main__':
    cli()
