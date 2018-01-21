import click
import boto3
import os

from getpass import getpass


@click.group()
def cli():
    pass


@cli.command('clone')
@click.option('-r', '--region')
@click.option('-p', '--profile')
@click.option('-m', '--mfa-serial')
@click.option('-o', '--output-profile')
@click.option('-d', '--duration', default=3600)
def clone(region, profile, mfa_serial, output_profile, duration):
    if output_profile is None:
        output_profile = '_{}'.format(profile)

    session = boto3.Session(
        profile_name=profile,
        region_name=region)
    client = session.client('sts')

    token_code = getpass('Input MFA code: ')
    response = client.get_session_token(
        DurationSeconds=duration,
        SerialNumber=mfa_serial,
        TokenCode=token_code
    )

    aws_secret_access_key = response['Credentials']['SecretAccessKey']
    aws_access_key_id = response['Credentials']['AccessKeyId']
    aws_session_token = response['Credentials']['SessionToken']

    configure_frm = 'aws configure --profile {aws_profile} set {name} {value}'

    os.system(configure_frm.format(
        aws_profile=output_profile,
        name='aws_secret_access_key',
        value=aws_secret_access_key,
    ))

    os.system(configure_frm.format(
        aws_profile=output_profile,
        name='aws_access_key_id',
        value=aws_access_key_id,
    ))

    os.system(configure_frm.format(
        aws_profile=output_profile,
        name='aws_session_token',
        value=aws_session_token,
    ))

    print 'Confirgured profile "{}"!'.format(output_profile)


@cli.command('clean-clones')
def clean_clones():
    pass


if __name__ == '__main__':
    cli()
