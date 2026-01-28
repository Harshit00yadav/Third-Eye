# =========================
# Project configuration
# =========================
SRC_DIR     := agents
OUT_DIR     := dropper
SRC_FILES   := $(wildcard $(SRC_DIR)/*.c) $(wildcard $(SRC_DIR)/downloader/*.c) $(wildcard $(SRC_DIR)/requests/*.c)

LINUX_CC    := gcc
WINDOWS_CC  := x86_64-w64-mingw32-gcc

LINUX_OUT   := $(OUT_DIR)/agent
WINDOWS_OUT := $(OUT_DIR)/agent.exe

WIN_LIB_     := /tmp/curl/lib/.libs/libcurl.a
WIN_LIB 		 := /usr/x86_64-w64-mingw32/curl-win/libcurl.a

CFLAGS      := -Wall -Wextra -O2
LFLAGS      := -lcurl
WFLAGS 			:= -DCURL_STATICLIB -lpsl -lws2_32 -liphlpapi -lcrypt32 -lsecur32 -lbcrypt -lz -static -static-libgcc

# =========================
# Default target (help)
# =========================
.DEFAULT_GOAL := help

# =========================
# Targets
# =========================
help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Available targets:"
	@echo "  linux     Compile for Linux"
	@echo "  windows   Cross-compile for Windows (mingw-w64)"
	@echo "  clean     Remove compiled binaries"
	@echo ""
	@echo "Directories:"
	@echo "  Source:   ./agents/"
	@echo "  Output:   ./dropper/"

linux: $(OUT_DIR)
	@echo "[*] Compiling for Linux..."
	$(LINUX_CC) $(SRC_FILES) $(CFLAGS) $(LFLAGS) -o $(LINUX_OUT)
	@echo "[+] Linux binary created at $(LINUX_OUT)"
	@echo "--[ SUCCESS ]--"

windows: $(OUT_DIR)
	@echo "[*] Compiling for Windows..."
	$(WINDOWS_CC) $(SRC_FILES) $(WIN_LIB) $(CFLAGS) $(WFLAGS) -o $(WINDOWS_OUT)
	@echo "[+] Windows binary created at $(WINDOWS_OUT)"
	@echo "--[ SUCCESS ]--"

$(OUT_DIR):
	@mkdir -p $(OUT_DIR)

clean:
	@echo "[*] Cleaning build artifacts..."
	@rm -f $(LINUX_OUT) $(WINDOWS_OUT)
	@echo "[+] Clean complete"

.PHONY: help linux windows clean
