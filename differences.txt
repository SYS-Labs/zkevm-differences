# Key Incompatibilities and Disallowed Opcodes in ZK Stack zkEVM

## 1. Incompatible Without Recompilation

If you take Ethereum‑compiled bytecode and run it on zkEVM, several opcodes will behave differently due to modified semantics in the zkEVM pipeline. These differences require you to recompile your Solidity code with a zkEVM‑aware compiler (such as **zksolc**) so that the low‑level details (like bytecode hashing, memory growth rules, constructor argument layout, etc.) are properly handled. Some examples:

### Contract Creation (Assembly Usage)

- **`CREATE` and `CREATE2`**  
  - On zkSYS, when you use the high‑level `new` operator, the compiler automatically handles bytecode hashing and constructor data layout by calling the `ContractDeployer` system contract behind the scenes.  
  - **However, if you use `CREATE` or `CREATE2` manually in inline assembly, the compiler cannot reliably inject the correct bytecode hash and system‑contract call logic.** This can lead to silently broken deployments where the contract code never actually gets deployed or gets deployed to an incorrect address.  
  - Some widely‑used libraries (e.g., OpenZeppelin, forge‑std) contain an assembly pattern for `CREATE2` that zksolc specifically accommodates, but **any variation** of that pattern is likely to fail.

### Deployment Data & Code Introspection

- **`CODESIZE` and `CODECOPY`**  
  - In Ethereum, `CODESIZE` and `CODECOPY` refer to the actual contract bytecode.  
  - On zkSYS, *during contract creation*, `CODESIZE` in the constructor returns the size of the constructor arguments (not the code), and `CODECOPY` effectively behaves more like `CALLDATACOPY` for those arguments.  
  - In runtime code, newer compiler backends may outright forbid `CODECOPY` because the actual bytecode is never directly available on zkEVM.

- **`DATASIZE`, `DATAOFFSET`, and `DATACOPY`**  
  - These refer to the "deployment header" (a 132‑byte region containing salt, hashed bytecode, etc.) plus any constructor arguments, rather than the raw contract code.  
  - As a result, any Ethereum‑compiled bytecode that expects to copy or introspect its own code using these instructions will break on zkSYS unless recompiled with the correct assumptions.

### External Calls & Memory Handling

- **`CALL`, `STATICCALL`, `DELEGATECALL`**  
  - On Ethereum, the EVM “pre‑allocates” memory if `outsize != 0`. On zkSYS, memory expansion and copying of return data happen *after* the call returns, which can yield different `msize()` values and potentially avoid some panics the EVM would trigger.  
  - Ether transfers also go through the `MsgValueSimulator` contract on zkSYS, so direct value sends are not the same as on Ethereum.

- **`CALLDATALOAD`, `CALLDATACOPY`, `RETURNDATACOPY`**  
  - zkSYS enforces slightly different bounds checks and loops internally, potentially causing unexpected panics or differences in memory usage if your bytecode is hand‑rolled.

- **`MSTORE` and `MLOAD`**  
  - Memory on zkSYS grows in **bytes**, not 32‑byte words. This also affects how `msize()` scales. Contracts that assume word‑based alignment from Ethereum can fail if they rely on exact memory sizes.

### External Code Access & Block Properties

- **`EXTCODEHASH`**  
  - On zkSYS, a contract’s code hash is a *versioned* sha3 hash, not the keccak256 of the raw bytecode as on Ethereum. Code‑based hash checks that assume Ethereum’s `EXTCODEHASH` behavior will not match.  

- **Block and transaction properties**  
  - **`COINBASE`** returns the bootloader’s address (`0x8001`) instead of the miner/validator address.  
  - **`DIFFICULTY`/`PREVRANDAO`** is a constant `2500000000000000`.  
  - **`BASEFEE`** is determined by zkSYS’s fee model—often 0.25 gwei but may rise under high L1 gas prices.  
  - **`TIMESTAMP` and `NUMBER`** can have different semantics compared to Ethereum (see the [ZKsync Docs on blocks](https://zksync.io/docs/reference/concepts/rollup/blocks) for details).

### Immutable Variables Handling

- **`SETIMMUTABLE` and `LOADIMMUTABLE`**  
  - The zkSYS compiler simulates immutables with a system contract called `ImmutableSimulator`. During deployment, the constructor returns an array of “index‑value” pairs for all immutables, which the simulator stores.  
  - If you rely on Ethereum’s direct rewriting of immutables in code, that logic will not hold; you must recompile so that `zksolc` instruments the correct calls to the system contract.

*In all these scenarios, recompilation with **zksolc** ensures your high‑level Solidity code produces zkEVM‑compatible bytecode that preserves the intended Ethereum‑like behavior.*

---

## 2. Disallowed by zkEVM

Some opcodes produce compile‑time errors in the zkSYS compiler and are unavailable regardless of whether you use inline assembly or Yul:

- **`SELFDESTRUCT`**  
  - Fully disabled on zkSYS (and considered harmful per [EIP-6049](https://eips.ethereum.org/EIPS/eip-6049)).

- **`CALLCODE`**  
  - Deprecated on Ethereum in favor of `DELEGATECALL` and entirely disallowed on zkSYS.

- **`PC`**  
  - Inaccessible in newer Solidity versions (>= 0.7.0) generally, and zkSYS treats it as an error in any case.

- **`EXTCODECOPY`**  
  - Directly reading another contract’s bytecode is not supported on zkSYS, so this opcode is disallowed.  

Any attempt to include these opcodes in your code (or in libraries that rely on them) will fail to compile under zkSYS.

---

## References

- [zkSync docs: EVM instructions differences](https://github.com/matter-labs/zksync-docs/blob/1.55.3/content/20.zksync-protocol/70.differences/10.evm-instructions.md)

