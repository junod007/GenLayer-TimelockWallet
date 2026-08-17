# {"Depends": "py-genlayer:j1b45ae8ynh2a9c9xn3b7qqh8m5q93hfwp7jqmwsfh8jpz09h6"}

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
    def get_owner(self) -> Address:
    return self.owner

    @gl.public.view
    def get_unlock_time(self) -> u256:
        return self.unlock_time

    @gl.public.view
    def is_locked(self) -> bool:
        return self.locked

    @gl.public.view
    def get_message(self) -> str:
        return self.message

    @gl.public.write
    def unlock(self):
        if gl.message.sender_address != self.owner:
            raise Exception("Only the owner can unlock this wallet")

        if not self.locked:
            raise Exception("Wallet is already unlocked")

        self.locked = False
        self.message = "Wallet has been unlocked"


