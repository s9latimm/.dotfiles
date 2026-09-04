import argparse
import datetime
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
# from cryptography.hazmat._oid import NameOID
from cryptography.hazmat.primitives.asymmetric import rsa


def main():
    parser = argparse.ArgumentParser(prog='rsa.py')
    parser.add_argument(
        '--format',
        type=str,
        choices=['PEM', 'SSH'],
        default='PEM',
    )
    parser.add_argument(
        '--certificate',
        action='store_true',
        default=True,
    )
    parser.add_argument(
        '--secrets',
        type=str,
        default='../secrets/',
    )
    parser.add_argument(
        '--prefix',
        type=str,
        default='s9rver',
    )
    parser.add_argument(
        '--unique',
        action='store_true',
        default=False,
    )
    print(parser.format_help())
    args = parser.parse_args()

    folder = args.prefix
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    if args.unique:
        folder += '_' + timestamp.strftime('%Y%m%d%H%M%S')
    secrets = (Path(__file__).parent / args.secrets / folder).resolve(strict=False)
    secrets.mkdir(exist_ok=True)

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    if args.format == 'PEM':
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    elif args.format == 'SSH':
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        )
    else:
        private_bytes = public_bytes = b''

    if args.certificate:
        subject = issuer = x509.Name([])

        builder = x509.CertificateBuilder()
        builder = builder.subject_name(subject)
        builder = builder.issuer_name(issuer)
        builder = builder.public_key(public_key)
        builder = builder.serial_number(x509.random_serial_number())
        builder = builder.not_valid_before(timestamp)
        builder = builder.not_valid_after(timestamp + datetime.timedelta(days=10))

        cert = builder.sign(private_key, hashes.SHA256())

        cert_bytes = cert.public_bytes(encoding=serialization.Encoding.PEM,)
        (secrets / 'id_rsa.cert.pem').write_bytes(private_bytes + cert_bytes)

    (secrets / 'id_rsa.pem').write_bytes(private_bytes)
    (secrets / 'id_rsa.pub.pem').write_bytes(public_bytes)


if __name__ == '__main__':
    main()
