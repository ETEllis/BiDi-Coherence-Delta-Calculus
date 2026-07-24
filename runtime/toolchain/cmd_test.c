/* `cdc test` — Phase C typed test runner (gate CT3 seed).
 *
 * Discovery is free: every CDC job already carries inline expectations, so
 * a source file IS its own test. For each file the runner selects every
 * execution mode its directives require, executes it through the legacy
 * runtime entry point in a forked child (isolation without host process
 * spawning — the child calls back into this same binary's linked runtime),
 * and classifies results with the Amendment A7 typed policy:
 *
 *   +1 commit  — "status=accepted" records
 *    0 hold    — "status=held" records; a hold is EXPECTED only when the
 *                job that held is declared with expect-status=held; any
 *                unexpected hold fails --gate
 *   nest       — nest-integration records, counted separately
 *   -1 fail    — a child that exits nonzero (violated expectation, crash)
 *
 * Counts are always reported separately; a merged pass total is forbidden
 * (A7). Execution is deterministic: files in argument order, modes in a
 * fixed family order, one child at a time.
 */
#define _POSIX_C_SOURCE 200809L

#include "cmd_test.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#include "../cdc_abi.h"

int cdc_native_main(int argc, char **argv);

typedef struct {
    long commit;
    long hold;
    long nest;
    long fail;
    long unexpected_hold;
    long expected_hold;
    long runs;
} test_counts;

/* mode selection: which runtime mode families a parsed unit requires */
typedef struct {
    const char *mode;
    const char *const directives[7];
} mode_rule;

static const mode_rule MODE_RULES[] = {
    {"run", {"flow", "commit", "nest", NULL}},
    {"compile", {"compile", NULL}},
    {"interpret", {"interpret", NULL}},
    {"prove", {"proof", NULL}},
    {"surface",
     {"guard", "trace", "measure", "policy", "bridge", "counter", NULL}},
    {"council", {"deliberate", NULL}},
    {"evolve", {"evolve", NULL}},
    {"universal", {"universal", NULL}},
};
enum { MODE_RULE_COUNT = sizeof(MODE_RULES) / sizeof(MODE_RULES[0]) };

static int program_contains(const cdc_program *program,
                            const char *const *directives) {
    size_t count = cdc_program_statement_count(program);
    size_t i;
    int d;
    for (i = 0; i < count; i++) {
        const char *directive =
            cdc_program_statement_directive(program, i);
        for (d = 0; directives[d]; d++) {
            if (directive && strcmp(directive, directives[d]) == 0) {
                return 1;
            }
        }
    }
    return 0;
}

/* Is `job` declared in this unit with expect-status=held? */
static int job_expects_hold(const cdc_program *program, const char *job) {
    size_t count = cdc_program_statement_count(program);
    size_t i;
    for (i = 0; i < count; i++) {
        const char *arg = cdc_program_statement_arg(program, i, 0);
        const char *expect;
        if (!arg || strcmp(arg, job) != 0) {
            continue;
        }
        expect = cdc_program_statement_attr(program, i, "expect-status");
        if (expect && strcmp(expect, "held") == 0) {
            return 1;
        }
    }
    return 0;
}

/* Extracts the job id from a runtime record line whose first token is
 * "<form>=<jobid>". Returns 0 if the line has no such shape. */
static int line_job_id(const char *line, char *out, size_t out_size) {
    const char *eq = strchr(line, '=');
    const char *space = strchr(line, ' ');
    size_t n;
    if (!eq || (space && eq > space)) {
        return 0;
    }
    n = space ? (size_t)(space - (eq + 1)) : strlen(eq + 1);
    if (n == 0 || n + 1 > out_size) {
        return 0;
    }
    memcpy(out, eq + 1, n);
    out[n] = '\0';
    return 1;
}

static void classify_output(FILE *fp, const cdc_program *program,
                            const char *file, const char *mode,
                            test_counts *counts, int verbose) {
    char line[4096];
    while (fgets(line, sizeof(line), fp)) {
        if (strstr(line, "status=accepted")) {
            counts->commit++;
        } else if (strstr(line, "status=held")) {
            char job[256];
            counts->hold++;
            if (line_job_id(line, job, sizeof(job)) &&
                job_expects_hold(program, job)) {
                counts->expected_hold++;
            } else {
                counts->unexpected_hold++;
                fprintf(stderr,
                        "cdc test: unexpected hold in %s (%s): %s", file,
                        mode, line);
            }
        }
        if (strncmp(line, "nest=", 5) == 0) {
            counts->nest++;
        }
        if (verbose) {
            fputs(line, stdout);
        }
    }
}

static int run_mode(const char *file, const char *mode,
                    const cdc_program *program, test_counts *counts,
                    int verbose) {
    const char *out_path = "build/cdc_test_child.txt";
    pid_t pid;
    int status;

    fflush(NULL);
    pid = fork();
    if (pid < 0) {
        fprintf(stderr, "cdc test: fork failed\n");
        return 0;
    }
    if (pid == 0) {
        char *child_argv[4];
        if (!freopen(out_path, "w", stdout) ||
            !freopen(out_path, "a", stderr)) {
            _exit(127);
        }
        child_argv[0] = (char *)"cdc";
        child_argv[1] = (char *)mode;
        child_argv[2] = (char *)file;
        child_argv[3] = NULL;
        /* exit (not _exit) so the child's redirected stdio flushes; no
         * atexit handlers exist in this binary. */
        exit(cdc_native_main(3, child_argv));
    }
    if (waitpid(pid, &status, 0) < 0) {
        fprintf(stderr, "cdc test: waitpid failed\n");
        return 0;
    }
    counts->runs++;
    {
        FILE *fp = fopen(out_path, "r");
        if (fp) {
            classify_output(fp, program, file, mode, counts, verbose);
            fclose(fp);
        }
    }
    if (!WIFEXITED(status) || WEXITSTATUS(status) != 0) {
        counts->fail++;
        fprintf(stderr, "cdc test: FAIL %s (%s) exit=%d\n", file, mode,
                WIFEXITED(status) ? WEXITSTATUS(status) : -1);
        {
            FILE *fp = fopen(out_path, "r");
            char line[4096];
            if (fp) {
                while (fgets(line, sizeof(line), fp)) {
                    fputs(line, stderr);
                }
                fclose(fp);
            }
        }
        return 0;
    }
    return 1;
}

int cdc_cmd_test(int argc, char **argv) {
    test_counts counts;
    int gate = 0, verbose = 0;
    int i, m;
    int first_file = 0;

    memset(&counts, 0, sizeof(counts));
    for (i = 0; i < argc; i++) {
        if (strcmp(argv[i], "--gate") == 0) {
            gate = 1;
        } else if (strcmp(argv[i], "--verbose") == 0) {
            verbose = 1;
        } else if (argv[i][0] == '-') {
            fprintf(stderr, "cdc test: unknown option %s\n", argv[i]);
            return 2;
        } else if (!first_file) {
            first_file = i;
        }
    }
    if (!first_file && (argc == 0 || argv[0][0] == '-')) {
        fprintf(stderr,
                "usage: cdc test [--gate] [--verbose] <files...>\n");
        return 2;
    }

    for (i = 0; i < argc; i++) {
        cdc_program *program = NULL;
        cdc_status status;
        if (argv[i][0] == '-') {
            continue;
        }
        status = cdc_program_parse(argv[i], NULL, 0, &program);
        if (status != CDC_OK) {
            fprintf(stderr, "cdc test: %s: %s\n", argv[i],
                    cdc_status_name(status));
            cdc_program_destroy(program);
            counts.fail++;
            continue;
        }
        for (m = 0; m < MODE_RULE_COUNT; m++) {
            if (program_contains(program, MODE_RULES[m].directives)) {
                run_mode(argv[i], MODE_RULES[m].mode, program, &counts,
                         verbose);
            }
        }
        cdc_program_destroy(program);
    }

    /* A7: separate counts, never a merged total; unexpected holds are gate
     * failures while expected holds are first-class equilibrium results. */
    printf("cdc test %s runs=%ld commit=%ld hold=%ld (expected=%ld "
           "unexpected=%ld) nest=%ld fail=%ld\n",
           counts.fail == 0 && counts.unexpected_hold == 0 ? "ok"
                                                           : "FAIL",
           counts.runs, counts.commit, counts.hold, counts.expected_hold,
           counts.unexpected_hold, counts.nest, counts.fail);
    if (counts.fail > 0) {
        return 1;
    }
    if (gate && counts.unexpected_hold > 0) {
        return 1;
    }
    return 0;
}
