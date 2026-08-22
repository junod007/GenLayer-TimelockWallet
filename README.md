# GenLayer Timelock Wallet

A simple time-locked wallet smart contract built on GenLayer.

The contract starts in a locked state and can only be unlocked by the wallet owner after the specified unlock time has been reached.

## Features

- Stores the wallet owner address
- Stores a predefined unlock timestamp
- Starts in a locked state
- Allows anyone to check the wallet owner
- Allows anyone to check the unlock time
- Allows anyone to check whether the wallet is locked
- Allows anyone to read the current wallet message
- Only the wallet owner can unlock the wallet
- Prevents unlocking before the specified unlock time
- Updates the wallet status after a successful unlock

## Smart Contract Functions

### Read Methods

#### `get_owner()`

Returns the address of the wallet owner.

#### `get_unlock_time()`

Returns the timestamp when the wallet can be unlocked.

#### `is_locked()`

Returns the current lock status.

- `true` → Wallet is locked
- `false` → Wallet has been unlocked

#### `get_message()`

Returns the current wallet message.

Initial message:

```text
Wallet is locked
