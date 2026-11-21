"""Two-pass assembler for the Hack machine language."""
import argparse
import re
import sys
from pathlib import Path

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010", "D": "0001100",
    "A": "0110000", "!D": "0001101", "!A": "0110001", "-D": "0001111",
    "-A": "0110011", "D+1": "0011111", "A+1": "0110111", "D-1": "0001110",
    "A-1": "0110010", "D+A": "0000010", "D-A": "0010011", "A-D": "0000111",
    "D&A": "0000000", "D|A": "0010101", "M": "1110000", "!M": "1110001",
    "-M": "1110011", "M+1": "1110111", "M-1": "1110010", "D+M": "1000010",
    "D-M": "1010011", "M-D": "1000111", "D&M": "1000000", "D|M": "1010101",
}
DEST = {"": "000", "M": "001", "D": "010", "MD": "011", "DM": "011",
        "A": "100", "AM": "101", "MA": "101", "AD": "110", "DA": "110",
        "AMD": "111", "ADM": "111", "MAD": "111", "MDA": "111",
        "DAM": "111", "DMA": "111"}
JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}
SYMBOL_RE = re.compile(r"^[A-Za-z_.$:][A-Za-z0-9_.$:]*$")


def predefined_symbols():
    symbols = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
               "SCREEN": 16384, "KBD": 24576}
    symbols.update({f"R{i}": i for i in range(16)})
    return symbols


def clean_lines(lines):
    result = []
    for line_number, raw in enumerate(lines, 1):
        text = raw.split("//", 1)[0]
        text = "".join(text.split())
        if text:
            result.append((line_number, text))
    return result


def assemble(lines):
    symbols = predefined_symbols()
    predefined = set(symbols)
    labels, variables, errors = {}, {}, []
    instructions = []

    # Pass one: labels map to instruction (ROM) addresses.
    for line_number, text in clean_lines(lines):
        if text.startswith("(") or text.endswith(")"):
            if not (text.startswith("(") and text.endswith(")") and
                    SYMBOL_RE.fullmatch(text[1:-1])):
                errors.append(f"Line {line_number}: invalid label")
                continue
            name = text[1:-1]
            if name in symbols:
                errors.append(f"Line {line_number}: duplicate or reserved label '{name}'")
            else:
                labels[name] = len(instructions)
                symbols[name] = len(instructions)
            continue
        instructions.append((line_number, text))

    # Pass two: translate instructions and assign RAM variables in first-use order.
    machine = []
    next_variable = 16
    for line_number, text in instructions:
        if text.startswith("@"):
            token = text[1:]
            if token.isdigit():
                value = int(token)
                if value > 32767:
                    errors.append(f"Line {line_number}: A-instruction value exceeds 32767")
                    continue
            elif SYMBOL_RE.fullmatch(token):
                if token not in symbols:
                    symbols[token] = next_variable
                    variables[token] = next_variable
                    next_variable += 1
                value = symbols[token]
            else:
                errors.append(f"Line {line_number}: invalid A-instruction")
                continue
            machine.append(f"{value:016b}")
            continue

        try:
            if text.count("=") > 1 or text.count(";") > 1:
                raise ValueError
            dest, remainder = (text.split("=", 1) if "=" in text else ("", text))
            comp, jump = (remainder.split(";", 1) if ";" in remainder else (remainder, ""))
            if dest not in DEST or comp not in COMP or jump not in JUMP:
                raise ValueError
            machine.append("111" + COMP[comp] + DEST[dest] + JUMP[jump])
        except ValueError:
            errors.append(f"Line {line_number}: invalid C-instruction")

    table = {"predefined": {k: predefined_symbols()[k] for k in predefined},
             "labels": labels, "variables": variables}
    return machine, errors, table


def write_symbols(path, table):
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for section in ("predefined", "labels", "variables"):
            stream.write(f"[{section}]\n")
            for name, address in sorted(table[section].items(), key=lambda item: (item[1], item[0])):
                stream.write(f"{name}={address}\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Assemble Hack .asm into .hack machine code.")
    parser.add_argument("source", type=Path, help="input .asm file")
    parser.add_argument("-o", "--output", type=Path, help="output .hack path (default: source with .hack)")
    parser.add_argument("--symbols", type=Path, help="symbol table path (default: symbols.txt beside output)")
    args = parser.parse_args(argv)
    if args.source.suffix.lower() != ".asm":
        parser.error("source file must have a .asm extension")
    output = args.output or args.source.with_suffix(".hack")
    symbol_path = args.symbols or output.parent / "symbols.txt"
    try:
        machine, errors, table = assemble(args.source.read_text(encoding="utf-8").splitlines())
    except OSError as exc:
        print(f"Cannot read {args.source}: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"{len(errors)} error(s); output not written.", file=sys.stderr)
        return 1
    output.write_text("\n".join(machine) + "\n", encoding="ascii", newline="\n")
    write_symbols(symbol_path, table)
    print(f"Wrote {len(machine)} instructions to {output}")
    print(f"Wrote symbol table to {symbol_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
