#include "downloader.h"
#include <stdio.h>
#include <stdlib.h>
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
	curl_easy_setopt(curl, CURLOPT_FAILONERROR, 1L);
	curl_easy_setopt(curl, CURLOPT_NOSIGNAL, 1L);
	curl_easy_setopt(curl, CURLOPT_SSL_VERIFYHOST, 0L);
	curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 0L);

	CURLcode rc = curl_easy_perform(curl);
	curl_easy_cleanup(curl);
	curl_global_cleanup();
	fclose(fp);
	return (rc == CURLE_OK) ? 0:1;
}
