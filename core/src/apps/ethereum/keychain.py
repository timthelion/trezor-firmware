from trezor import wire

from . import CURVE, networks

from apps.common import HARDENED
from apps.common.seed import get_keychain

if False:
    from trezor.messages.EthereumSignTx import EthereumSignTx
    from apps.common.seed import MsgIn, MsgOut, Handler, HandlerWithKeychain


def with_keychain_from_path(
    func: HandlerWithKeychain[MsgIn, MsgOut]
) -> Handler[MsgIn, MsgOut]:
    async def wrapper(ctx: wire.Context, msg: MsgIn) -> MsgOut:
        assert hasattr(msg, "address_n")

        if len(msg.address_n) < 2:
            raise wire.DataError("Forbidden key path")
        slip44_hardened = msg.address_n[1]
        if slip44_hardened not in networks.all_slip44_ids_hardened():
            raise wire.DataError("Forbidden key path")
        namespace = CURVE, [44 | HARDENED, slip44_hardened]
        keychain = await get_keychain(ctx, [namespace])
        with keychain:
            return await func(ctx, msg, keychain)

    return wrapper


def with_keychain_from_chain_id(
    func: HandlerWithKeychain[EthereumSignTx, MsgOut]
) -> Handler[EthereumSignTx, MsgOut]:
    async def wrapper(ctx: wire.Context, msg: EthereumSignTx) -> MsgOut:
        if msg.chain_id is None:
            msg.chain_id = 0
        info = networks.by_chain_id(msg.chain_id)
        if info is None:
            raise wire.DataError("Unsupported chain id")

        slip44 = info.slip44
        if networks.is_wanchain(msg.chain_id, msg.tx_type):
            slip44 = networks.SLIP44_WANCHAIN

        namespace = CURVE, [44 | HARDENED, slip44 | HARDENED]
        keychain = await get_keychain(ctx, [namespace])
        with keychain:
            return await func(ctx, msg, keychain)

    return wrapper
