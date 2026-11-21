# NAND2Tetris Capstone — Make the Computer Draw a Box

**Student:** Sushant Kumar · **Roll:** 2501010290 · **K:** 90

**Course:** Nand to Tetris I (ETCCNT301)

## Objective and dimensions

The Hack computer runs `Box.asm` and draws a solid black rectangle while any keyboard key is pressed, then clears those screen words after release. For K=90, the top row is 90, the height is 20 rows, and the width is `16 × ((90 mod 4) + 1) = 48` pixels. That is three 16-pixel words per row. A screen row has 32 words, so the first word is `16384 + 32 × 90 = 19264`. The program writes only the three words at the left edge of each of those 20 rows.

## Hardware files

`Computer.hdl` connects `ROM32K`, `CPU`, and `Memory`. `CPU.hdl` contains the A and D registers, ALU, destination control, jump logic, and program counter. `Memory.hdl` decodes the address into RAM, screen, or keyboard regions. The implementation uses the standard built-in NAND2Tetris chips (`ARegister`, `DRegister`, `ALU`, `PC`, `RAM16K`, `Screen`, `Keyboard`, and mux/gate chips); the course hardware simulator supplies them. No pre-existing lab HDL repository was present in the supplied workspace.

## Assembler and symbol table

`assembler.py` does two passes. The first strips comments and whitespace, records labels at their ROM instruction addresses, and excludes label declarations from instruction counts. The second encodes A- and C-instructions, resolves predefined symbols and labels, and allocates variables from RAM address 16 in first-use order. For this assignment's `K mod 3 = 0`, it writes predefined symbols, labels, and variables to `symbols.txt` beside the output file.

Run from this directory:

```powershell
python assembler.py Box.asm
python assembler.py path\to\Program.asm -o path\to\Program.hack --symbols path\to\symbols.txt
```

The default output is the input filename with `.hack`; the default symbol table is `symbols.txt` in the output directory.

## Verification status

- Generated `Box.hack` with this project's `assembler.py`: 49 instructions.
- Checked the box address, row count, and per-row word count against the PDF formulas. The touched addresses range from 19264 to 19874, in 20 groups of three words with 29 untouched words between rows.
- Assembled the supplied reference `Add.asm`, `Max.asm`, `Rect.asm`, and `Pong.asm`. Each machine-code instruction line matches the corresponding `.hack` file committed in the linked reference repository. This is a comparison to the repository files; it does **not** establish that those files came from the official assembler.
- The official `CPU.tst`, `Memory.tst`, and `Computer*.tst` scripts and the Hardware Simulator / CPU Emulator were not available in this workspace. Those simulator tests and the visual keyboard interaction remain unverified. Do not report them as passing or use screenshots from the K=55 reference repository as evidence for this K=90 result.

### Manual simulator steps

1. Open the official Hardware Simulator and load `CPU.hdl`, then run `CPU.tst`; repeat with `Memory.hdl` / `Memory.tst` and `Computer.hdl` with each supplied computer test script. The required `.tst` and `.cmp` files must be available locally.
2. Open the CPU Emulator, load `Box.hack`, and run the program. Hold a key: the rectangle should appear at the left edge beginning at row 90, extending 48 pixels by 20 rows. Release the key: it should clear.
3. Capture your own simulator output and emulator view for the report. No screenshots are included because none were generated in this workspace.

## Report outline and honest mistake note

1. Title and identity: Sushant Kumar, 2501010290, K=90, course and project.
2. Computer architecture: describe the three HDL files and note the built-in chips used.
3. Assembler: explain the two passes and show the generated symbol table.
4. Box calculation and code: show row 90, 20 rows, 48 pixels / 3 words, and starting address 19264.
5. Results: insert your own Hardware Simulator test screenshots and CPU Emulator screenshot after completing the manual steps above; list outcomes accurately.
6. Mistake fixed paragraph (based on the actual adaptation): “The reference program was written for K=55 and used a starting address and four screen words per row for a 64-pixel box. Carrying those constants into my submission would draw the wrong box. I recalculated the start as `16384 + 32×90 = 19264` and the width as 48 pixels, then changed the row loop to write three words for each of 20 rows.”

## Viva practice

1. **What does the assembler do?** It converts Hack assembly mnemonics into 16-bit machine instructions.
2. **Why are there two passes?** The first pass discovers label addresses; the second can then resolve forward and backward label references.
3. **What is an A-instruction?** `@value` loads a 15-bit address or constant into the A register.
4. **What is a C-instruction?** It tells the ALU what to compute, which registers to load, and whether to jump.
5. **Where do variables go?** Starting at RAM address 16, in order of first use.
6. **What is a label address?** Its ROM address, counting machine instructions but not label declarations.
7. **Why does 48 pixels use three words?** One screen word stores 16 adjacent pixels.
8. **How did you find the first screen word?** `SCREEN + 32×row = 16384 + 32×90 = 19264`.
9. **How does the program clear the box?** When KBD is zero it writes 0 to the same 60 screen words; when nonzero it writes -1.
10. **What does the symbol table contain?** Predefined symbols plus the labels and variables used by the assembled source, with their addresses.

## Submission and Git workflow

This supplied workspace was empty and had no `.git` directory, so it is not yet inside your existing lab repository. Move/copy this `capstone` directory into that repository, then from the repository root review and commit only these project files:

```powershell
git status --short
git add capstone/CPU.hdl capstone/Memory.hdl capstone/Computer.hdl capstone/assembler.py capstone/Box.asm capstone/Box.hack capstone/symbols.txt capstone/README.md
git diff --cached
git commit -m "Add NAND2Tetris K=90 capstone"
git push
```

Submit the 3–4 page report and your verified screenshots through ZOSIMA as instructed.
