#ifndef CDC_ABI_H
#define CDC_ABI_H

#include <stddef.h>
#include <stdint.h>

/* cdc_abi — the stable embeddable C boundary (Amendment A2).
 *
 * ABI version: 1.0. cdc_abi_version() returns (major << 16) | minor.
 * Additions bump the minor version; any breaking change bumps the major
 * version and renames nothing silently. The CLI, daemons, SDK bindings, and
 * tests consume this boundary; nothing outside runtime/ may include the
 * internal frontend headers.
 *
 * Ownership and lifetime
 *   Every object returned through an out-parameter is owned by the caller
 *   and released with the matching *_destroy function (bytes with
 *   cdc_bytes_free). Destroy functions accept NULL. Handles are independent:
 *   destroying a cdc_program does not invalidate results derived from it.
 *
 * Thread safety
 *   A cdc_program is immutable after parse; concurrent reads are safe.
 *   cdc_runtime and cdc_result are single-thread objects; guard external
 *   sharing. No global state is mutated by this surface.
 *
 * Determinism
 *   Parsing, diagnostics, canonical serialization, and result serialization
 *   are bit-deterministic for identical inputs on any platform.
 *
 * Allocation and errors
 *   All allocation failures surface as CDC_ERR_MEMORY; no function aborts
 *   the process or prints. Every function returns cdc_status; out-values are
 *   NULL/0 on failure.
 *
 * Availability at ABI 1.0
 *   Parse, diagnostics, canonical bytes, and result serialization are fully
 *   implemented. cdc_runtime_execute and cdc_runtime_verify are declared for
 *   ABI shape stability but return CDC_ERR_STATE with an explanatory result
 *   until the execution surface lands (Phase C); they never partially
 *   execute. This is a typed fail-closed contract, not undefined behavior.
 */

#define CDC_ABI_VERSION_MAJOR 1
#define CDC_ABI_VERSION_MINOR 0

typedef enum {
    CDC_OK = 0,
    CDC_ERR_ARGUMENT = 1, /* bad parameter combination */
    CDC_ERR_IO = 2,       /* file unreadable */
    CDC_ERR_PARSE = 3,    /* source rejected; diagnostics available */
    CDC_ERR_MEMORY = 4,   /* allocation failure */
    CDC_ERR_STATE = 5,    /* operation not available in this object state */
} cdc_status;

typedef struct cdc_program cdc_program;
typedef struct cdc_runtime cdc_runtime;
typedef struct cdc_result cdc_result;

uint32_t cdc_abi_version(void);
const char *cdc_status_name(cdc_status status);

/* Parses a source unit. Exactly one of `path` and `buffer` must be non-NULL
 * (`length` applies to `buffer`). A handle is returned even when the source
 * is rejected (status CDC_ERR_PARSE) so diagnostics can be read; only
 * CDC_ERR_ARGUMENT / CDC_ERR_IO / CDC_ERR_MEMORY return no handle.
 *
 * I/O contract (2026-07-23 review): a path must name a readable REGULAR
 * file. Directories, FIFOs, and devices return CDC_ERR_IO without blocking
 * and without a handle — never an empty accepted program. Mid-read errors
 * return CDC_ERR_IO; allocation failure is always CDC_ERR_MEMORY, never
 * remapped. A zero-byte regular file is a VALID unit with zero statements
 * (CDC_OK). Sources above the parser bound (64 MiB) return CDC_ERR_IO. */
cdc_status cdc_program_parse(const char *path, const char *buffer,
                             size_t length, cdc_program **out);

/* Number of statements in the parsed unit (0 when rejected early). */
size_t cdc_program_statement_count(const cdc_program *program);

/* Number of error diagnostics recorded for the unit. */
size_t cdc_program_error_count(const cdc_program *program);

/* Produces the unit's diagnostics as a result object (possibly empty). */
cdc_status cdc_program_diagnostics(const cdc_program *program,
                                   cdc_result **out);

/* Canonical grammar-1 serialization of an accepted unit. Rejected units
 * return CDC_ERR_STATE. Bytes are caller-owned (cdc_bytes_free). */
cdc_status cdc_program_canonical_bytes(const cdc_program *program,
                                       char **out_bytes, size_t *out_length);

cdc_status cdc_runtime_create(cdc_runtime **out);

/* Declared at ABI 1.0; functional from the Phase C execution surface.
 * Until then both return CDC_ERR_STATE and, when `out` is non-NULL, a
 * result explaining the gap. They never partially execute. */
cdc_status cdc_runtime_execute(cdc_runtime *runtime,
                               const cdc_program *program,
                               const char *entry_job, cdc_result **out);
cdc_status cdc_runtime_verify(cdc_runtime *runtime,
                              const cdc_program *program, cdc_result **out);

/* Number of error entries carried by a result. */
size_t cdc_result_error_count(const cdc_result *result);

/* Serializes a result as deterministic JSON:
 *   {"abi":"1.0","errors":N,"diagnostics":["...", ...]}
 * Bytes are caller-owned (cdc_bytes_free). */
cdc_status cdc_result_serialize(const cdc_result *result, char **out_bytes,
                                size_t *out_length);

void cdc_program_destroy(cdc_program *program);
void cdc_runtime_destroy(cdc_runtime *runtime);
void cdc_result_destroy(cdc_result *result);
void cdc_bytes_free(char *bytes);

#endif
