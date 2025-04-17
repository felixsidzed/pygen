import pygen

# Helper function to print binary data in a hex format
def printBytes(data: bytearray):
	for i in range(0, len(data), 16):
		chunk = data[i:i+16]
		hex = ' '.join(f"{b:02x}" for b in chunk)
		print(f"{i:04x}: {hex}")

def main():
	# Create a COFF file generator
	gen: pygen.COFFGenerator = pygen.COFFGenerator()

	# Create a `.text' section
	text: pygen.COFFSection = gen.section(
		".text",
		0x60000020 # CODE | EXECUTE | READ
	)

	# Emit some assembly instructions
	# Below is a Windows x64 `Hello, World!' program

	# Common function prologue
	# Since we aren't modifying the stack you can remove this
	text.emit(b"\x55")         # push rbp
	text.emit(b"\x48\x89\xe5") # mov rbp, rsp

	lea = text.emit(b"\x48\x8d\x0d\x00\x00\x00\x00") + 3 # lea rcx, [rip + aHello]
	call = text.emit(b"\xe8\x00\x00\x00\x00") + 1 		 # call print
	text.emit(b"\x5d")									 # pop rbp
	text.emit(b"\xc3")									 # ret

	# Create an `.rdata' section for read-only data (strings in our case)
	rdata: pygen.COFFSection = gen.section(".rdata", 0x40000040)

	# Add a null-terminated `Hello, World!' string
	stringOffset = rdata.emit(b"Hello, World!\n\0")

	# Define a symbol for the main function so the linker knows where our entry point is
	gen.symbol("main", 0, 1, 0x20)

	# Define a symbol for our `Hello, World!` string
	gen.symbol("aHello", stringOffset, 2, 0x0)  # 2 = .rdata section

	# Define an external symbol called "print"
	gen.symbol("print", 0, 0, 0x20)

	# Add relocation for the LEA instruction (to point to the string in .rdata)
	text.reloc(lea, 1, 4)  # 1 is the symbol index of "aHello"

	# Add relocation for the CALL instruction (to the external "print" function)
	text.reloc(call, 2, 4)  # 2 refers to symbol index of "print"

	# Generate the final binary object file
	coff = gen.emit()

	# Save it to disk
	with open("build/test.o", "wb") as f:
		f.write(coff)

	# Print out the binary contents in hex for debugging
	print(f"=== [module 'test'] ({len(coff)} bytes) ===")
	printBytes(coff)

	# To successfully run the generated file:
	# - Make sure you are using a 64-bit Windows machines
	# - Make sure you are linking against lib/io.lib
	# - It is recommended to use the MSVC linker

if __name__ == "__main__":
	main()
