# zkevm-differences

**zkevm-differences** is a tool for programmatically hunting opcode incompatibilities between standard Ethereum Virtual Machine (EVM) implementations and certain zkEVM variants.

## Overview

The script [`check_opcodes.py`](check_opcodes.py) fetches EVM opcode data from a remote URL and compares it against another remote (or inline) source of zkEVM opcodes. Any differences found are printed to the console and can be summarized in [`differences.md`](differences.md).

## Getting Started

### Prerequisites

- **Python 3.7+**  
- **pip** (Python package manager)  
- An active internet connection (the script fetches CSV data from remote URLs).

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SYS-Labs/zkevm-differences.git
   cd zkevm-differences
   ```
2. **Install the required Python libraries:**
   ```bash
   pip install requests
   ```
   _Note: Currently, `requests` is the primary dependency._

### Usage

1. **Run the comparison script:**
   ```bash
   python check_opcodes.py
   ```
2. **Review the output:**  
   The script prints any differences found between the EVM and zkEVM opcodes to the terminal.

3. **Check [`differences.md`](differences.md):**  
   - This file may include additional notes or context.
   - Feel free to update it with your findings.

## Contributing

Contributions are welcome! If you find issues or have ideas for improving the script:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Submit a pull request.

Alternatively, you can open an issue to discuss any proposed changes.

## License

This project is released under the [MIT License](LICENSE). Feel free to use and modify the code under the terms of the license.