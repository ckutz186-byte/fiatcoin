from fiatcoin.core.hash import sha256d
from fiatcoin.core.readable import computer
from io import BytesIO
from fiatcoin.core.serialize import stream_serialize_vlq


just_believe_in_me = (
    b"You buy a piece of paradise\n"
    b"You buy a piece of me\n"
    b"I'll get you everything you wanted\n"
    b"I'll get you everything you need\n"
    b"Don't need to believe in hereafter\n"
    b"Just believe in me"
)

f = BytesIO()
stream_serialize_vlq(f, len(just_believe_in_me))
f.write(just_believe_in_me)
lyric_sig = f.getvalue().hex()

genesis_previous_hash = sha256d(just_believe_in_me)

genesis_block_data = computer(
    '0000000000000000000000000000000000000000000000000000000000000000'  # prev block
    '0000616c35621abdf928185b74d57985cea7ff2d66ef318c58ec7ea8dd01ed0890'  # merkle root
    '28604e7f'        # timestamp
    '31010000'        # bits (difficulty)
    '00000000'        # nonce
    '0000000000000000000000000000000000000000000000000000000000000000'  # padding/extra
    '3aea13176dbcbf621055bdb3d6a138be4b73229d8584cb380e1dd1bbe1cedd42'  # tx hash root
    '8200000000000000000000000000000000000000000000000000000000000000'
    'e38ee41a6b0f6584fe8b95bd8c8d7b4d6db961fa5c2a6fafe72ea1533dd2838b'
    '0100010000000000000000000000000000000000000000000000000000000000'
    '000000000000000001'  # tx count (1)
    + lyric_sig +       # your lyric as varint-prefixed "signature"
    '000000003b9aca00'  # tx output (10 BTC for example)
    '02aac3faad6ddc26ec4674328741498fe74bdb0d8e49a22473a02370e53d69b0'
    '079819d5ac3f0cd36f25578eb042ad2a7b59f84a0b5f622e41ac982f478e8cb259'
)
