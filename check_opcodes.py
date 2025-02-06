#!/usr/bin/env python3
import sys
from web3 import Web3
from evmdasm import EvmBytecode

# ANSI escape codes for colors
RED_BG = "\033[41m"
RESET = "\033[0m"


def main():
    if len(sys.argv) < 3:
        print("Usage: python check_opcodes.py <rpc-url> <contract-address>")
        sys.exit(1)

    node_url = sys.argv[1]
    contract_address = sys.argv[2]

    # Connect to the Ethereum node
    w3 = Web3(Web3.HTTPProvider(node_url))
    if not w3.is_connected():
        print(f"Error: Unable to connect to Ethereum node at {node_url}")
        sys.exit(1)

    # Retrieve contract bytecode
    bytecode = w3.eth.get_code(contract_address).hex()
    if bytecode in ("0x", ""):
        print(f"No bytecode found at contract address {contract_address}")
        sys.exit(1)

    print(f"Disassembling contract at {contract_address}")
    print(f"Bytecode (first 60 chars): {bytecode[:60]}...\n")

    # Disassemble the bytecode using evmdasm
    evm_bytecode = EvmBytecode(bytecode)
    instructions = evm_bytecode.disassemble()

    # Define opcodes that require recompilation (incompatible) and those fully disallowed
    incompatible_set = {
        "CREATE", "CREATE2",
        "CODESIZE", "CODECOPY",
        "DATASIZE", "DATAOFFSET", "DATACOPY",
        "CALL", "STATICCALL", "DELEGATECALL",
        "CALLDATALOAD", "CALLDATACOPY", "RETURNDATACOPY",
        "MSTORE", "MLOAD",
        "EXTCODEHASH",
        "COINBASE", "DIFFICULTY", "PREVRANDAO", "BASEFEE", "TIMESTAMP", "NUMBER",
        "SETIMMUTABLE", "LOADIMMUTABLE"
    }
    disallowed_set = {"SELFDESTRUCT", "CALLCODE", "PC", "EXTCODECOPY"}

    # Dictionaries to collect found opcodes and their positions
    found_incompatible = {}
    found_disallowed = {}

    # Scan through each instruction
    for instr in instructions:
        opcode = instr.name
        if opcode in disallowed_set:
            found_disallowed.setdefault(opcode, []).append(instr.address)
        elif opcode in incompatible_set:
            found_incompatible.setdefault(opcode, []).append(instr.address)

    # Print the results for disallowed opcodes with a red background prefix
    if found_disallowed:
        print(f"{RED_BG}[DISALLOWED]{RESET} The following disallowed opcodes were found:")
        for opcode, positions in found_disallowed.items():
            positions_str = ", ".join(hex(pos) for pos in positions)
            print(f" - {opcode} at positions: {positions_str}")
        for opcode, positions in found_opcodes.items():
            positions_str = ", ".join(hex(pos) for pos in positions)
            print(f" - {opcode} at positions: {positions_str}")

        # Add the note about disallowed opcodes
        print("\n## opcodes Disallowed by zkEVM:\n")
        print("- **`SELFDESTRUCT`**  ")
        print("  - Fully disabled on zkSYS (and considered harmful per [EIP-6049](https://eips.ethereum.org/EIPS/eip-6049)).\n")
        print("- **`CALLCODE`**  ")
        print("  - Deprecated on Ethereum in favor of `DELEGATECALL` and entirely disallowed on zkSYS.\n")
        print("- **`PC`**  ")
        print("  - Inaccessible in newer Solidity versions (>= 0.7.0) generally, and zkSYS treats it as an error in any case.\n")
        print("- **`EXTCODECOPY`**  ")
        print("  - Directly reading another contract’s bytecode is not supported on zkSYS, so this opcode is disallowed.\n")
        print("\nAny attempt to include these opcodes in your code (or in libraries that rely on them) will fail to compile under zkSYS.")
    else:
        print("No disallowed opcodes were found in the contract bytecode.")

    # Print the results for incompatible opcodes with a prefix indicating recompilation is needed
    if found_incompatible:
        print("\n[INCOMPATIBLE] – recompile the contract with a zkEVM‑aware compiler for the following opcodes:")
        for opcode, positions in found_incompatible.items():
            positions_str = ", ".join(hex(pos) for pos in positions)
            print(f" - {opcode} at positions: {positions_str}")
    else:
        print("\nNo incompatible opcodes were found in the contract bytecode.")

if __name__ == "__main__":
    main()

