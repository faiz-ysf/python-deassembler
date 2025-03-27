import dis
import sys
import io
import types

def decompile_source(input_file):
    try:
        # Read source code
        with open(input_file, "r", encoding="utf-8") as file:
            source_lines = file.readlines()

        # Compile source to bytecode
        compiled_code = compile("".join(source_lines), "<script>", "exec")

        # Prepare output buffer
        output = io.StringIO()

        # Detailed Bytecode Mapping
        output.write("Detailed Bytecode Mapping:\n")
        output.write("-" * 120 + "\n")
        output.write("Line  Source Code                                        | Bytecode                       | Description\n")
        output.write("-" * 120 + "\n")

        # Extract all instructions
        all_instructions = list(dis.get_instructions(compiled_code))

        # Create line-based instruction mapping
        line_bytecode_map = {}
        for instr in all_instructions:
            if instr.starts_line:
                line_bytecode_map.setdefault(instr.starts_line, []).append(instr)

        # Process line-by-line bytecode
        for line_num, line in enumerate(source_lines, 1):
            line = line.rstrip()
            bytecodes = line_bytecode_map.get(line_num, [])
            
            if bytecodes:
                for bytecode in bytecodes:
                    # Customize description based on opcode
                    if bytecode.opname == "LOAD_CONST":
                        if isinstance(bytecode.argval, types.CodeType):
                            desc = f"({bytecode.offset} -> <code object {bytecode.argval.co_name} at {hex(id(bytecode.argval))}, file \"<script>\", line {line_num}>)"
                        else:
                            desc = f"({bytecode.offset} -> {repr(bytecode.argval)})"
                    else:
                        desc = f"({bytecode.offset} -> {bytecode.argrepr or ''})"
                    
                    output.write(f"{line_num:<5} {line:<50} | {bytecode.opname:<30} | {desc}\n")

        # Function Bytecode Details
        output.write("\n\nFunction Bytecode Details:\n")
        output.write("-" * 120 + "\n")

        # Find and process function code objects
        function_objects = [
            const for const in compiled_code.co_consts 
            if isinstance(const, types.CodeType)
        ]

        for func_code in function_objects:
            # Function header
            output.write(f"\nFunction: {func_code.co_name}\n")
            output.write("-" * 50 + "\n")

            # Capture function bytecode
            func_bytecode = list(dis.Bytecode(func_code))

            # Prepare column widths
            col_width_src = 50
            col_width_byte = 30
            col_width_desc = 30

            # Print function bytecode header
            header = f"{'Line':<5} {'Source Code':<{col_width_src}} | {'Bytecode':<{col_width_byte}} | {'Description':<{col_width_desc}}\n"
            output.write(header)
            output.write("-" * len(header) + "\n")

            # Get source lines for the function
            try:
                func_source_lines = [
                    (lineno, source_lines[lineno - 1].rstrip()) 
                    for _, _, lineno in func_code.co_lines() 
                    if lineno is not None
                ]
            except Exception:
                func_source_lines = []

            # Match bytecode with source lines
            for src, byte in zip(func_source_lines, func_bytecode):
                byte_desc = f"({byte.arg} -> {byte.argrepr})" if byte.arg is not None else ""
                output.write(f"{src[0]:<5} {src[1]:<{col_width_src}} | {byte.opname:<{col_width_byte}} | {byte_desc:<{col_width_desc}}\n")

        # Print the final output
        print(output.getvalue())

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_filename>")
        sys.exit(1)

    # Decompile the source file
    decompile_source(sys.argv[1])

if __name__ == "__main__":
    main()
