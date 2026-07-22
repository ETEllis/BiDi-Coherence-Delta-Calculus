#include "cmd_verify.h"

#include <stdio.h>
#include <string.h>

#include "../cdc_abi.h"

static int verify_parse(int argc, char **argv) {
    int i;
    size_t statements = 0;
    for (i = 0; i < argc; i++) {
        cdc_program *program = NULL;
        cdc_status status = cdc_program_parse(argv[i], NULL, 0, &program);
        if (status == CDC_ERR_PARSE) {
            cdc_result *result = NULL;
            fprintf(stderr, "cdc verify: %s rejected\n", argv[i]);
            if (cdc_program_diagnostics(program, &result) == CDC_OK) {
                char *json = NULL;
                size_t length = 0;
                if (cdc_result_serialize(result, &json, &length) == CDC_OK) {
                    fwrite(json, 1, length, stderr);
                    fputc('\n', stderr);
                    cdc_bytes_free(json);
                }
                cdc_result_destroy(result);
            }
            cdc_program_destroy(program);
            return 1;
        }
        if (status != CDC_OK) {
            fprintf(stderr, "cdc verify: %s: %s\n", argv[i],
                    cdc_status_name(status));
            cdc_program_destroy(program);
            return 1;
        }
        statements += cdc_program_statement_count(program);
        cdc_program_destroy(program);
    }
    printf("cdc verify parse ok files=%d statements=%zu\n", argc,
           statements);
    return 0;
}

int cdc_cmd_verify(int argc, char **argv) {
    if (argc >= 1 && strcmp(argv[0], "--parse") == 0) {
        if (argc < 2) {
            fprintf(stderr, "cdc verify --parse: no files given\n");
            return 2;
        }
        return verify_parse(argc - 1, argv + 1);
    }
    fprintf(stderr,
            "cdc verify: full contract evaluation lands with Phase C "
            "(gate toolchain-verify-parity); available now: "
            "cdc verify --parse <files...>\n");
    return 3;
}
