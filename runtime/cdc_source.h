#ifndef CDC_SOURCE_H
#define CDC_SOURCE_H

#include <stddef.h>

void cdc_source_fail(const char *message);

int cdc_starts_with(const char *s, const char *prefix);
void cdc_trim(char *s);
void cdc_trim_newline(char *s);
void cdc_strip_comment(char *s);
void cdc_first_token_after(const char *line, const char *prefix, char *out, size_t out_size);

int cdc_read_attr(const char *line, const char *key, char *out, size_t out_size);
double cdc_read_double_attr(const char *line, const char *key, double fallback);
int cdc_read_int_attr(const char *line, const char *key, int fallback);
void cdc_copy_attr(const char *line, const char *key, char *out, size_t out_size, const char *fallback);

int cdc_close_enough(double actual, double expected, double tolerance);
void cdc_expect_string(const char *actual, const char *expected, const char *message);
void cdc_expect_int(int actual, int expected, const char *message);
void cdc_expect_double(double actual, double expected, double tolerance, const char *message);

#endif
