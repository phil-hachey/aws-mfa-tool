import click
import boto3
import os

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

    if token_code is None and mfa_serial:
        token_code = getpass('Input MFA code: ')

    response = client.get_session_token(
        DurationSeconds=duration,
        SerialNumber=mfa_serial,
        TokenCode=token_code
    )

    if not skip_save:
        if save_output_profile is None:
            save_output_profile = '_{}'.format(profile)

        aws_secret_access_key = response['Credentials']['SecretAccessKey']
        aws_access_key_id = response['Credentials']['AccessKeyId']
        aws_session_token = response['Credentials']['SessionToken']

        configure_frm = 'aws configure --profile {aws_profile} set {name} {value}'

        os.system(configure_frm.format(
            aws_profile=save_output_profile,
            name='aws_secret_access_key',
            value=aws_secret_access_key,
        ))

        os.system(configure_frm.format(
            aws_profile=save_output_profile,
            name='aws_access_key_id',
            value=aws_access_key_id,
        ))

        os.system(configure_frm.format(
            aws_profile=save_output_profile,
            name='aws_session_token',
            value=aws_session_token,
        ))

        print 'Saved credentials profile "{}"!'.format(save_output_profile)

    print response


if __name__ == '__main__':
    cli()
