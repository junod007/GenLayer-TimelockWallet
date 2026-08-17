# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *


class GenLayerTimelockWallet(gl.Contract):
    owner: Address
    unlock_time: u256
    locked: bool
    message: str

    def __init__(self, unlock_time: u256):
        self.owner = gl.message.sender_address
        self.unlock_time = unlock_time
        self.locked = True
        self.message = "Wallet is locked"

    @gl.public.view
    def get_owner(self) -> str:
        return self.owner.as_hex

    @gl.public.view
    def get_unlock_time(self) -> u256:
        return self.unlock_time

    @gl.public.view
    def is_locked(self) -> bool:
        return self.locked

    @gl.public.view
    def get_status(self) -> str:
        return self.message

    @gl.public.write
    def update_message(self, new_message: str) -> None:
        if gl.message.sender_address != self.owner:
            raise gl.vm.UserError("Only the owner can update the wallet")

        self.message = new_message
