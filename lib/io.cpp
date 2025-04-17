#ifdef _WIN32
#include <windows.h>

extern "C" void print(const char* message) {
	DWORD written;
	HANDLE stdout = GetStdHandle(STD_OUTPUT_HANDLE);
	if (stdout != INVALID_HANDLE_VALUE && message) {
		WriteConsoleA(stdout, message, lstrlenA(message), &written, nullptr);
	}
}
#else
#error "libio is not yet available on non-windows machines"
#endif
