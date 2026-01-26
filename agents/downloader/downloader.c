#include "downloader.h"
#include <stdio.h>
#include <stdlib.h>
#ifdef _WIN32
// ----------windows--------------
#include <windows.h>
#include <winhttp.h>

int download_file(const char *url, const char *output_path){
	wchar_t wurl[1024];
	wchar_t wfile[512];

	MultiByteToWideChar(CP_UTF8, 0, url, -1, wurl, 1024);
	MultiByteToWideChar(CP_UTF8, 0, output_path, -1, wfile, 512);

	URL_COMPONENTS uc;
	ZeroMemory(&uc, sizeof(uc));
	uc.dwStructSize = sizeof(uc);
	uc.dwSchemeLength    = (DWORD)-1;
	uc.dwHostNameLength  = (DWORD)-1;
	uc.dwUrlPathLength   = (DWORD)-1;
	uc.dwExtraInfoLength = (DWORD)-1;

	if (!WinHttpCrackUrl(wurl, 0, 0, &uc)) {
		fprintf(stderr, "CrackUrl failed\n");
		return 1;
	}

	wchar_t host[256];
	wcsncpy(host, uc.lpszHostName, uc.dwHostNameLength);
	host[uc.dwHostNameLength] = L'\0';

	BOOL https = (uc.nScheme == INTERNET_SCHEME_HTTPS);

	HINTERNET session = WinHttpOpen(
		L"Mozilla/5.0",
		WINHTTP_ACCESS_TYPE_NO_PROXY,
		WINHTTP_NO_PROXY_NAME,
		WINHTTP_NO_PROXY_BYPASS,
		0
	);
	if (!session) return 1;

	DWORD protocols =
		WINHTTP_FLAG_SECURE_PROTOCOL_TLS1 |
		WINHTTP_FLAG_SECURE_PROTOCOL_TLS1_1 |
		WINHTTP_FLAG_SECURE_PROTOCOL_TLS1_2;

	WinHttpSetOption(
		session,
		WINHTTP_OPTION_SECURE_PROTOCOLS,
		&protocols,
		sizeof(protocols)
	);

	WINHTTP_PROXY_INFO proxy = {
		WINHTTP_ACCESS_TYPE_NO_PROXY,
		WINHTTP_NO_PROXY_NAME,
		WINHTTP_NO_PROXY_BYPASS
	};
	WinHttpSetOption(
		session,
		WINHTTP_OPTION_PROXY,
		&proxy,
		sizeof(proxy)
	);

	HINTERNET connect = WinHttpConnect(session, host, uc.nPort, 0);
	if (!connect) {
		WinHttpCloseHandle(session);
		return 1;
	}

	wchar_t full_path[1024];
	wcscpy(full_path, uc.lpszUrlPath);
	if (uc.lpszExtraInfo)
		wcscat(full_path, uc.lpszExtraInfo);

	HINTERNET request = WinHttpOpenRequest(
		connect,
		L"GET",
		full_path,
		NULL,
		WINHTTP_NO_REFERER,
		WINHTTP_DEFAULT_ACCEPT_TYPES,
		https ? WINHTTP_FLAG_SECURE : 0
	);
	if (!request) {
		WinHttpCloseHandle(connect);
		WinHttpCloseHandle(session);
		return 1;
	}

	if (!WinHttpSendRequest(request, NULL, 0, NULL, 0, 0, 0)) {
		DWORD err = GetLastError();
		fprintf(stderr, "SendRequest Error: %lu\n", err);
		WinHttpCloseHandle(request);
		WinHttpCloseHandle(connect);
		WinHttpCloseHandle(session);
		return 1;
	}

	if (!WinHttpReceiveResponse(request, NULL)) {
		fprintf(stderr, "ReceiveResponse Error\n");
		WinHttpCloseHandle(request);
		WinHttpCloseHandle(connect);
		WinHttpCloseHandle(session);
		return 1;
	}

	FILE *fp = _wfopen(wfile, L"wb");
	if (fp){
		BYTE buffer[4096];
		DWORD read = 0;
		while (WinHttpReadData(request, buffer, sizeof(buffer), &read) && read) {
			fwrite(buffer, 1, read, fp);
		}

		fclose(fp);
	}
	WinHttpCloseHandle(request);
	WinHttpCloseHandle(connect);
	WinHttpCloseHandle(session);
	return 0;
}
#else
// ----------linux-----------------
#include <curl/curl.h>

static size_t write_cb(void *ptr, size_t size, size_t nmemb, void *stream){
	return fwrite(ptr, size, nmemb, (FILE *)stream);
}

int download_file(const char *url, const char *output_path){
	FILE *fp = fopen(output_path, "wb");
	if (!fp) {
		fprintf(stderr, "Unable to open file path\n");
		return 1;
	}
	curl_global_init(CURL_GLOBAL_DEFAULT);
	CURL *curl = curl_easy_init();
	if (!curl) return 1;

	curl_easy_setopt(curl, CURLOPT_URL, url);
	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_cb);
	curl_easy_setopt(curl, CURLOPT_WRITEDATA, fp);
	curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
	curl_easy_setopt(curl, CURLOPT_TIMEOUT, 30L);

	CURLcode rc = curl_easy_perform(curl);
	curl_easy_cleanup(curl);
	curl_global_cleanup();
	fclose(fp);
	return (rc == CURLE_OK) ? 0:1;
}
#endif

