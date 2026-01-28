#include <stdio.h>
#ifndef HTTPREQUEST_H
#define HTTPREQUEST_H

int http_get(const char *url, const char *user_agent, char **resp_data, size_t *resp_size);

#endif
