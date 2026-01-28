#include "http_request.h"
#include <curl/curl.h>
#include <stdlib.h>
#include <string.h>

struct mem {
	char *data;
	size_t size;
};

static size_t write_cb(void *ptr, size_t size, size_t nmemb, void *userdata){
	size_t bytes = size * nmemb;
	struct mem *m = userdata;
	char *tmp = realloc(m->data, m->size + bytes + 1);
	if (!tmp)
		return 0;
	m->data = tmp;
	memcpy(m->data + m->size, ptr, bytes);
	m->size += bytes;
	m->data[m->size] = '\0';
	return bytes;
}

int http_get(const char *url, const char *user_agent, char **resp_data, size_t *resp_size){
	*resp_data = NULL;
	*resp_size = 0;

	curl_global_init(CURL_GLOBAL_DEFAULT);

	CURL *curl = curl_easy_init();
	if (!curl)
		return 1;

	struct mem m = {0};

	curl_easy_setopt(curl, CURLOPT_URL, url);
	curl_easy_setopt(curl, CURLOPT_USERAGENT, user_agent);
	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_cb);
	curl_easy_setopt(curl, CURLOPT_WRITEDATA, &m);

	curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
	curl_easy_setopt(curl, CURLOPT_TIMEOUT, 30L);
	curl_easy_setopt(curl, CURLOPT_FAILONERROR, 1L);
	curl_easy_setopt(curl, CURLOPT_NOSIGNAL, 1L);
	curl_easy_setopt(curl, CURLOPT_SSL_VERIFYHOST, 0L);
	curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 0L);

	CURLcode rc = curl_easy_perform(curl);
	curl_easy_cleanup(curl);
	curl_global_cleanup();

	if (rc != CURLE_OK) {
		fprintf(stderr, "curl error: %s\n", curl_easy_strerror(rc));
		free(m.data);
		return 1;
	}

	*resp_data = m.data;
	*resp_size = m.size;
	return 0;
}
