/* cdc — unified toolchain driver (Amendment A9: dispatcher + command
 * modules). This layer consumes ONLY the stable ABI (cdc_abi.h); it never
 * includes internal frontend or runtime headers. Commands land in their
 * amendment phases; unimplemented commands fail closed with a typed notice
 * and exit code 3 rather than pretending. */
#include <stdio.h>
#include <string.h>

#include "../cdc_abi.h"
#include "cmd_verify.h"

static int cmd_version(void) {
    uint32_t version = cdc_abi_version();
    printf("cdc abi=%u.%u grammar=1\n", version >> 16, version & 0xffffu);
    return 0;
}

static int cmd_unavailable(const char *name, const char *phase) {
    fprintf(stderr, "cdc %s: lands with %s (see CDC_TOOLCHAIN_PLAN.md)\n",
            name, phase);
    return 3;
}

static void usage(FILE *stream) {
    fputs("usage: cdc <command> [args]\n"
          "commands: verify version run test install build x\n",
          stream);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        usage(stderr);
        return 2;
    }
    if (strcmp(argv[1], "verify") == 0) {
        return cdc_cmd_verify(argc - 2, argv + 2);
    }
    if (strcmp(argv[1], "version") == 0) {
        return cmd_version();
    }
    if (strcmp(argv[1], "run") == 0 || strcmp(argv[1], "test") == 0) {
        return cmd_unavailable(argv[1], "Phase C");
    }
    if (strcmp(argv[1], "install") == 0 || strcmp(argv[1], "build") == 0 ||
        strcmp(argv[1], "x") == 0) {
        return cmd_unavailable(argv[1], "Phase I");
    }
    if (strcmp(argv[1], "--help") == 0 || strcmp(argv[1], "help") == 0) {
        usage(stdout);
        return 0;
    }
    fprintf(stderr, "cdc: unknown command '%s'\n", argv[1]);
    usage(stderr);
    return 2;
}
