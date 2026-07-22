#ifndef CDC_PARSER_H
#define CDC_PARSER_H

#include "cdc_ast.h"
#include "cdc_diagnostic.h"

/* Grammar-1 parser (Amendment A1). Accepts exactly the grammar-0 language:
 * the statement stream a valid file produces here corresponds one-to-one to
 * the declarations the legacy loader collects, and every input the legacy
 * loader rejects produces at least one error diagnostic here (differential
 * gate CT1). The parser never exits and never prints; all failures are typed
 * diagnostics. Structural "end" lines and blank/comment lines are
 * represented/skipped exactly as grammar 0 does.
 *
 * Grammar-0 rejection conditions replicated as errors:
 *   CDC011 trailing escape            CDC012 unclosed quote
 *   CDC020 unknown directive          CDC021 missing required first argument
 *   CDC022 duplicate framework key (within the parsed unit)
 * Bounds: CDC010 line too long, CDC013 too many tokens, CDC900 allocation.
 */

/* Parses an in-memory buffer. Returns 1 on completion (check diags->errors
 * for acceptance), 0 on allocation failure (program left valid but partial).
 * `file` is recorded for spans and dump records (basename as given). */
int cdc_program_parse_buffer(const char *buffer, size_t length,
                             const char *file, cdc_program *out,
                             cdc_diag_list *diags);

/* Reads and parses a file from disk. Returns 1 on completion, 0 when the
 * file cannot be read (diagnostic recorded) or allocation fails. */
int cdc_program_parse_file(const char *path, cdc_program *out,
                           cdc_diag_list *diags);

#endif
