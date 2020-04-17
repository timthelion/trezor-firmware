import trezorconfig as config  # noqa: F401
import trezorio as io  # noqa: F401

if False:
    import trezorio.fatfs as fatfs
else:
    fatfs = io.fatfs
