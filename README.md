# GenLayer Timelock Wallet

A simple smart contract built on GenLayer that demonstrates a basic wallet locking mechanism.

The contract starts in a locked state and can only be unlocked by the wallet owner.

## Features

- Stores the wallet owner address
- Stores an unlock time value
- Starts in a locked state
- Allows anyone to check the wallet status
- Allows anyone to read the wallet message
- Allows anyone to view the owner address
- Only the owner can unlock the wallet
- Prevents the wallet from being unlocked more than once

## Smart Contract

The contract provides the following methods:

### Read Methods

#### `get_owner()`

Returns the address of the wallet owner.

#### `get_unlock_time()`

Returns the configured unlock time.

#### `is_locked()`

Returns the current lock status.

- `true` = wallet is locked
- `false` = wallet has been unlocked

#### `get_message()`

Returns the current wallet message.

Initial message:

```text
Wallet is locked
