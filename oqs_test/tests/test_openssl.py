import helpers
import os
import sys
import time

kex_algs_master_111 = [
    'oqs_kem_default',
    'p256_oqs_kem_default',
##### OQS_TEMPLATE_FRAGMENT_KEX_ALGS_MASTER_START
    # post-quantum key exchanges
    'frodo640aes','frodo640shake','frodo976aes','frodo976shake','frodo1344aes','frodo1344shake','extrahope512','kyber512','kyber768','kyber1024','sikep434','sikep503','sikep610','sikep751',
    # post-quantum + classical key exchanges
    'p256_frodo640aes','p256_frodo640shake','p256_frodo976aes','p256_frodo976shake','p256_frodo1344aes','p256_frodo1344shake','p256_extrahope512','p256_kyber512','p256_kyber768','p256_kyber1024','p256_sikep434','p256_sikep503','p256_sikep610','p256_sikep751',
##### OQS_TEMPLATE_FRAGMENT_KEX_ALGS_MASTER_END
    ]
sig_algs_master_111 = [
    'rsa:3072',
    'ecdsa',
##### OQS_TEMPLATE_FRAGMENT_SIG_ALGS_MASTER_START
    # post-quantum signatures
    'oqs_sig_default','dilithium2','dilithium3','dilithium4','picnicl1fs','picnic2l1fs','qteslapi','qteslapiii',
    # post-quantum + classical signatures
    'p256_oqs_sig_default','rsa3072_oqs_sig_default','p256_dilithium2','rsa3072_dilithium2','p384_dilithium4','p256_picnicl1fs','rsa3072_picnicl1fs','p256_picnic2l1fs','rsa3072_picnic2l1fs','p256_qteslapi','rsa3072_qteslapi','p384_qteslapiii',
##### OQS_TEMPLATE_FRAGMENT_SIG_ALGS_MASTER_END
    ]

kex_algs = kex_algs_master_111
sig_algs = sig_algs_master_111

def test_gen_keys():
    global sig_algs
    for sig_alg in sig_algs:
        yield (gen_keys, sig_alg)

def gen_keys(sig_alg):
    if sig_alg == 'ecdsa':
        # generate curve parameters
        helpers.run_subprocess(
            [
                'apps/openssl', 'ecparam',
                '-out', 'secp384r1.pem',
                '-name', 'secp384r1'
            ],
            os.path.join('..')
        )
        # generate CA key and cert
        helpers.run_subprocess(
            [
                'apps/openssl', 'req', '-x509', '-new',
                '-newkey', 'ec:secp384r1.pem',
                '-keyout', '{}_CA.key'.format(sig_alg),
                '-out', '{}_CA.crt'.format(sig_alg),
                '-nodes',
                '-subj', '/CN=oqstest_CA',
                '-days', '365',
                '-config', 'apps/openssl.cnf'
            ],
            os.path.join('..')
        )
        # generate server CSR
        helpers.run_subprocess(
            [
                'apps/openssl', 'req', '-new',
                '-newkey', 'ec:secp384r1.pem',
                '-keyout', '{}_srv.key'.format(sig_alg),
                '-out', '{}_srv.csr'.format(sig_alg),
                '-nodes',
                '-subj', '/CN=oqstest_server',
                '-config', 'apps/openssl.cnf'
            ],
            os.path.join('..')
        )
    else:
        # generate CA key and cert
        helpers.run_subprocess(
            [
                'apps/openssl', 'req', '-x509', '-new',
                '-newkey', sig_alg,
                '-keyout', '{}_CA.key'.format(sig_alg),
                '-out', '{}_CA.crt'.format(sig_alg),
                '-nodes',
                '-subj', '/CN=oqstest_CA',
                '-days', '365',
                '-config', 'apps/openssl.cnf'
            ],
            os.path.join('..')
        )
        # generate server CSR
        helpers.run_subprocess(
            [
                'apps/openssl', 'req', '-new',
                '-newkey', sig_alg,
                '-keyout', '{}_srv.key'.format(sig_alg),
                '-out', '{}_srv.csr'.format(sig_alg),
                '-nodes',
                '-subj', '/CN=oqstest_server',
                '-config', 'apps/openssl.cnf'
            ],
            os.path.join('..')
        )
    # generate server cert
    helpers.run_subprocess(
        [
            'apps/openssl', 'x509', '-req',
            '-in', '{}_srv.csr'.format(sig_alg),
            '-out', '{}_srv.crt'.format(sig_alg),
            '-CA', '{}_CA.crt'.format(sig_alg),
            '-CAkey', '{}_CA.key'.format(sig_alg),
            '-CAcreateserial',
            '-days', '365'
        ],
        os.path.join('..')
    )

def test_connection():
    global sig_algs, kex_algs
    port = 23567
    for sig_alg in sig_algs:
        for kex_alg in kex_algs:
            yield(run_connection, sig_alg, kex_alg, port)
            port = port + 1

def run_connection(sig_alg, kex_alg, port):
    cmd = os.path.join('oqs_test', 'scripts', 'do_openssl-111.sh');
    helpers.run_subprocess(
        [cmd],
        os.path.join('..'),
        env={'SIGALG': sig_alg, 'KEXALG': kex_alg, 'PORT': str(port)}
    )

if __name__ == '__main__':
    try:
        import nose2
        nose2.main()
    except ImportError:
        import nose
        nose.runmodule()
