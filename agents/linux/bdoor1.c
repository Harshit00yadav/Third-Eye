#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <curl/curl.h>

struct memory {
	char *data;
	size_t size;
};

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

int main(int argc, char **argv){
	if (argc < 2){
		printf("Usage: bdoor <url>\n");
		return 1;
	}
	char *URL = argv[1];
	struct memory response = {0};

	CURL *curl;
	CURLcode status_code;
	curl = curl_easy_init();
	if (curl == NULL){
		fprintf(stderr, "curl init failed\n");
		return 1;
	}
	curl_easy_setopt(curl, CURLOPT_URL, URL);
	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, callback);
	curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&response);
	while (1){
		response.size = 0;
		status_code = curl_easy_perform(curl);
		if (status_code != CURLE_OK){
			fprintf(stderr, "Error: %s\n", curl_easy_strerror(status_code));
			sleep(10);
			continue;
		}
		printf("response: %s\n", response.data);
		printf("size: %zu\ncapacity: %zu\n", response.size, strlen(response.data));
		sleep(5);
	}
	free(response.data);
	curl_easy_cleanup(curl);
	return 0;
}
