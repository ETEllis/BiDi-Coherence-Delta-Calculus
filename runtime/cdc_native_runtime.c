#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_FIELDS 16
#define MAX_MODULES 64
#define MAX_CELLS 256
#define MAX_CHANNELS 256
#define MAX_STEPS 128
#define MAX_COMPILE_JOBS 32
#define MAX_PROOF_JOBS 32
#define MAX_COUNCILS 32
#define MAX_DELIBERATIONS 32
#define MAX_EVOLUTIONS 32
#define LINE_MAX_BYTES 1024
#define PI 3.14159265358979323846

typedef enum {
    STEP_FLOW,
    STEP_COMMIT,
    STEP_NEST
} StepKind;

typedef struct {
    char name[64];
    double dt;
    double gain;
    double deadband;
} Field;

typedef struct {
    char name[64];
    char field[64];
    char parent[64];
    double belief;
    double prior;
    double precision;
    double action_gain;
} Module;

typedef struct {
    char name[64];
    char module[64];
    double theta;
    double amplitude;
    double omega;
    char latch;
    int has_latch;
} Cell;

typedef struct {
    char source[64];
    char target[64];
    double weight;
    double delay;
    double angle;
    char lines[64];
} Channel;

typedef struct {
    StepKind kind;
    char id[64];
    char field[64];
    char module[64];
    char parent[64];
    char child[64];
    double duration;
    double tolerance;
    char expect_theta_cell[64];
    double expect_theta;
    char expect_trits[64];
    char expect_balance[32];
    int has_expect_theta;
    int has_expect_parent_belief;
    int has_expect_child_prior;
    double expect_parent_belief;
    double expect_child_prior;
} Step;

typedef struct {
    char id[64];
    char source[128];
    int expect_ops;
    int expect_flow;
    int expect_commit;
    int expect_nest;
} CompileJob;

typedef struct {
    char id[64];
    char carrier[64];
    int arity;
    int expect_total;
    int expect_admissible;
    int expect_localized;
    int expect_saturated;
    int expect_catalan;
} ProofJob;

typedef struct {
    char id[64];
    char field[64];
    char members[256];
    int quorum;
    char expect_decision[32];
    char expect_dyadic[32];
    char expect_triadic[32];
} Council;

typedef struct {
    char id[64];
    char council[64];
} Deliberation;

typedef struct {
    char id[64];
    char source[128];
    char output[128];
    char coordinate[32];
    char append_witness[64];
    char expect_contains[64];
} EvolutionJob;

typedef struct {
    Field fields[MAX_FIELDS];
    Module modules[MAX_MODULES];
    Cell cells[MAX_CELLS];
    Channel channels[MAX_CHANNELS];
    Step steps[MAX_STEPS];
    CompileJob compile_jobs[MAX_COMPILE_JOBS];
    ProofJob proof_jobs[MAX_PROOF_JOBS];
    Council councils[MAX_COUNCILS];
    Deliberation deliberations[MAX_DELIBERATIONS];
    EvolutionJob evolutions[MAX_EVOLUTIONS];
    int field_count;
    int module_count;
    int cell_count;
    int channel_count;
    int step_count;
    int compile_job_count;
    int proof_job_count;
    int council_count;
    int deliberation_count;
    int evolution_count;
} Runtime;

static void fail(const char *message) {
    fprintf(stderr, "cdc-native-runtime: %s\n", message);
    exit(1);
}

static int starts_with(const char *s, const char *prefix) {
    return strncmp(s, prefix, strlen(prefix)) == 0;
}

static void trim(char *s) {
    size_t n;
    char *p = s;
    while (*p && isspace((unsigned char)*p)) {
        p++;
    }
    if (p != s) {
        memmove(s, p, strlen(p) + 1);
    }
    n = strlen(s);
    while (n > 0 && isspace((unsigned char)s[n - 1])) {
        s[n - 1] = '\0';
        n--;
    }
}

static void strip_comment(char *s) {
    char *hash = strchr(s, '#');
    if (hash) {
        *hash = '\0';
    }
    trim(s);
}

static void first_token_after(const char *line, const char *prefix, char *out, size_t out_size) {
    const char *p = line + strlen(prefix);
    size_t i = 0;
    while (*p && !isspace((unsigned char)*p)) {
        if (i + 1 >= out_size) {
            fail("token too long");
        }
        out[i++] = *p++;
    }
    out[i] = '\0';
}

static int read_attr(const char *line, const char *key, char *out, size_t out_size) {
    char needle[64];
    const char *p;
    size_t i = 0;
    snprintf(needle, sizeof(needle), "%s=", key);
    p = strstr(line, needle);
    if (!p) {
        return 0;
    }
    p += strlen(needle);
    while (*p && !isspace((unsigned char)*p)) {
        if (i + 1 >= out_size) {
            fail("attribute too long");
        }
        out[i++] = *p++;
    }
    out[i] = '\0';
    return 1;
}

static double read_double_attr(const char *line, const char *key, double fallback) {
    char value[64];
    if (!read_attr(line, key, value, sizeof(value))) {
        return fallback;
    }
    return atof(value);
}

static int read_int_attr(const char *line, const char *key, int fallback) {
    char value[64];
    if (!read_attr(line, key, value, sizeof(value))) {
        return fallback;
    }
    return atoi(value);
}

static void copy_attr(const char *line, const char *key, char *out, size_t out_size, const char *fallback) {
    if (!read_attr(line, key, out, out_size)) {
        snprintf(out, out_size, "%s", fallback);
    }
}

static Field *find_field(Runtime *rt, const char *name) {
    for (int i = 0; i < rt->field_count; i++) {
        if (strcmp(rt->fields[i].name, name) == 0) {
            return &rt->fields[i];
        }
    }
    return NULL;
}

static Module *find_module(Runtime *rt, const char *name) {
    for (int i = 0; i < rt->module_count; i++) {
        if (strcmp(rt->modules[i].name, name) == 0) {
            return &rt->modules[i];
        }
    }
    return NULL;
}

static Council *find_council(Runtime *rt, const char *name) {
    for (int i = 0; i < rt->council_count; i++) {
        if (strcmp(rt->councils[i].id, name) == 0) {
            return &rt->councils[i];
        }
    }
    return NULL;
}

static Cell *find_cell(Runtime *rt, const char *name) {
    for (int i = 0; i < rt->cell_count; i++) {
        if (strcmp(rt->cells[i].name, name) == 0) {
            return &rt->cells[i];
        }
    }
    return NULL;
}

static int find_cell_index(Runtime *rt, const char *name) {
    for (int i = 0; i < rt->cell_count; i++) {
        if (strcmp(rt->cells[i].name, name) == 0) {
            return i;
        }
    }
    return -1;
}

static int modules_share_field(Runtime *rt, const char *module_name, const char *field_name) {
    Module *module = find_module(rt, module_name);
    return module && strcmp(module->field, field_name) == 0;
}

static int cell_in_field(Runtime *rt, const Cell *cell, const char *field_name) {
    return modules_share_field(rt, cell->module, field_name);
}

static char trit_from_theta(double theta, double deadband) {
    double kappa = cos(theta);
    if (kappa > deadband) {
        return '+';
    }
    if (kappa < -deadband) {
        return '-';
    }
    return '0';
}

static int trit_value(char trit) {
    if (trit == '+') {
        return 1;
    }
    if (trit == '-') {
        return -1;
    }
    return 0;
}

static int close_enough(double a, double b, double tolerance) {
    return fabs(a - b) <= tolerance;
}

static void add_field(Runtime *rt, const char *line) {
    Field *field;
    if (rt->field_count >= MAX_FIELDS) {
        fail("too many fields");
    }
    field = &rt->fields[rt->field_count++];
    first_token_after(line, "field ", field->name, sizeof(field->name));
    field->dt = read_double_attr(line, "dt", 0.01);
    field->gain = read_double_attr(line, "gain", 1.0);
    field->deadband = read_double_attr(line, "deadband", 0.5);
}

static void add_module(Runtime *rt, const char *line) {
    Module *module;
    if (rt->module_count >= MAX_MODULES) {
        fail("too many modules");
    }
    module = &rt->modules[rt->module_count++];
    first_token_after(line, "module ", module->name, sizeof(module->name));
    copy_attr(line, "field", module->field, sizeof(module->field), "");
    copy_attr(line, "parent", module->parent, sizeof(module->parent), "");
    module->belief = read_double_attr(line, "belief", 0.0);
    module->prior = read_double_attr(line, "prior", 0.0);
    module->precision = read_double_attr(line, "precision", 1.0);
    module->action_gain = read_double_attr(line, "action-gain", 1.0);
    if (!find_field(rt, module->field)) {
        fail("module references unknown field");
    }
}

static void add_cell(Runtime *rt, const char *line) {
    Cell *cell;
    if (rt->cell_count >= MAX_CELLS) {
        fail("too many cells");
    }
    cell = &rt->cells[rt->cell_count++];
    first_token_after(line, "cell ", cell->name, sizeof(cell->name));
    copy_attr(line, "module", cell->module, sizeof(cell->module), "");
    cell->theta = read_double_attr(line, "theta", 0.0);
    cell->amplitude = read_double_attr(line, "amplitude", 1.0);
    cell->omega = read_double_attr(line, "omega", 0.0);
    cell->latch = '0';
    cell->has_latch = 0;
    if (!find_module(rt, cell->module)) {
        fail("cell references unknown module");
    }
}

static void add_channel(Runtime *rt, const char *line) {
    Channel *channel;
    char arrow[16];
    if (rt->channel_count >= MAX_CHANNELS) {
        fail("too many channels");
    }
    channel = &rt->channels[rt->channel_count++];
    if (sscanf(line, "channel %63s %15s %63s", channel->source, arrow, channel->target) != 3 ||
        strcmp(arrow, "->") != 0) {
        fail("channel syntax must be: channel source -> target");
    }
    channel->weight = read_double_attr(line, "weight", 1.0);
    channel->delay = read_double_attr(line, "delay", 0.0);
    channel->angle = read_double_attr(line, "angle", 0.0);
    copy_attr(line, "lines", channel->lines, sizeof(channel->lines), "*");
    if (!find_cell(rt, channel->source) || !find_cell(rt, channel->target)) {
        fail("channel references unknown source or target cell");
    }
}

static void parse_expect_theta(Step *step, const char *line) {
    char value[128];
    char *colon;
    if (!read_attr(line, "expect-theta", value, sizeof(value))) {
        return;
    }
    colon = strchr(value, ':');
    if (!colon) {
        fail("expect-theta must be cell:value");
    }
    *colon = '\0';
    snprintf(step->expect_theta_cell, sizeof(step->expect_theta_cell), "%s", value);
    step->expect_theta = atof(colon + 1);
    step->has_expect_theta = 1;
}

static void add_step(Runtime *rt, const char *line, StepKind kind, const char *prefix) {
    Step *step;
    char value[64];
    if (rt->step_count >= MAX_STEPS) {
        fail("too many reducer steps");
    }
    step = &rt->steps[rt->step_count++];
    memset(step, 0, sizeof(*step));
    step->kind = kind;
    first_token_after(line, prefix, step->id, sizeof(step->id));
    step->duration = read_double_attr(line, "duration", 0.0);
    step->tolerance = read_double_attr(line, "tolerance", 0.000001);
    copy_attr(line, "field", step->field, sizeof(step->field), "");
    copy_attr(line, "module", step->module, sizeof(step->module), "");
    copy_attr(line, "parent", step->parent, sizeof(step->parent), "");
    copy_attr(line, "child", step->child, sizeof(step->child), "");
    copy_attr(line, "expect-trits", step->expect_trits, sizeof(step->expect_trits), "");
    copy_attr(line, "expect-balance", step->expect_balance, sizeof(step->expect_balance), "");
    parse_expect_theta(step, line);
    if (read_attr(line, "expect-parent-belief", value, sizeof(value))) {
        step->expect_parent_belief = atof(value);
        step->has_expect_parent_belief = 1;
    }
    if (read_attr(line, "expect-child-prior", value, sizeof(value))) {
        step->expect_child_prior = atof(value);
        step->has_expect_child_prior = 1;
    }
}

static void add_compile_job(Runtime *rt, const char *line) {
    CompileJob *job;
    if (rt->compile_job_count >= MAX_COMPILE_JOBS) {
        fail("too many compile jobs");
    }
    job = &rt->compile_jobs[rt->compile_job_count++];
    memset(job, 0, sizeof(*job));
    first_token_after(line, "compile ", job->id, sizeof(job->id));
    copy_attr(line, "source", job->source, sizeof(job->source), "");
    job->expect_ops = read_int_attr(line, "expect-ops", -1);
    job->expect_flow = read_int_attr(line, "expect-flow", -1);
    job->expect_commit = read_int_attr(line, "expect-commit", -1);
    job->expect_nest = read_int_attr(line, "expect-nest", -1);
}

static void add_proof_job(Runtime *rt, const char *line) {
    ProofJob *job;
    if (rt->proof_job_count >= MAX_PROOF_JOBS) {
        fail("too many proof jobs");
    }
    job = &rt->proof_jobs[rt->proof_job_count++];
    memset(job, 0, sizeof(*job));
    first_token_after(line, "proof ", job->id, sizeof(job->id));
    copy_attr(line, "carrier", job->carrier, sizeof(job->carrier), "");
    job->arity = read_int_attr(line, "arity", 0);
    job->expect_total = read_int_attr(line, "expect-total", -1);
    job->expect_admissible = read_int_attr(line, "expect-admissible", -1);
    job->expect_localized = read_int_attr(line, "expect-localized", -1);
    job->expect_saturated = read_int_attr(line, "expect-saturated", -1);
    job->expect_catalan = read_int_attr(line, "expect-catalan", -1);
}

static void add_council(Runtime *rt, const char *line) {
    Council *council;
    if (rt->council_count >= MAX_COUNCILS) {
        fail("too many councils");
    }
    council = &rt->councils[rt->council_count++];
    memset(council, 0, sizeof(*council));
    first_token_after(line, "council ", council->id, sizeof(council->id));
    copy_attr(line, "field", council->field, sizeof(council->field), "");
    copy_attr(line, "members", council->members, sizeof(council->members), "");
    copy_attr(line, "expect-decision", council->expect_decision, sizeof(council->expect_decision), "");
    copy_attr(line, "expect-dyadic", council->expect_dyadic, sizeof(council->expect_dyadic), "");
    copy_attr(line, "expect-triadic", council->expect_triadic, sizeof(council->expect_triadic), "");
    council->quorum = read_int_attr(line, "quorum", 1);
}

static void add_deliberation(Runtime *rt, const char *line) {
    Deliberation *deliberation;
    if (rt->deliberation_count >= MAX_DELIBERATIONS) {
        fail("too many deliberations");
    }
    deliberation = &rt->deliberations[rt->deliberation_count++];
    memset(deliberation, 0, sizeof(*deliberation));
    first_token_after(line, "deliberate ", deliberation->id, sizeof(deliberation->id));
    copy_attr(line, "council", deliberation->council, sizeof(deliberation->council), "");
}

static void add_evolution(Runtime *rt, const char *line) {
    EvolutionJob *job;
    if (rt->evolution_count >= MAX_EVOLUTIONS) {
        fail("too many evolution jobs");
    }
    job = &rt->evolutions[rt->evolution_count++];
    memset(job, 0, sizeof(*job));
    first_token_after(line, "evolve ", job->id, sizeof(job->id));
    copy_attr(line, "source", job->source, sizeof(job->source), "");
    copy_attr(line, "output", job->output, sizeof(job->output), "");
    copy_attr(line, "coordinate", job->coordinate, sizeof(job->coordinate), "");
    copy_attr(line, "append-witness", job->append_witness, sizeof(job->append_witness), "");
    copy_attr(line, "expect-contains", job->expect_contains, sizeof(job->expect_contains), "");
}

static void parse_source(Runtime *rt, const char *path) {
    FILE *fp = fopen(path, "r");
    char line[LINE_MAX_BYTES];
    if (!fp) {
        fail("could not open native reducer source");
    }
    memset(rt, 0, sizeof(*rt));
    while (fgets(line, sizeof(line), fp)) {
        strip_comment(line);
        if (line[0] == '\0' || strcmp(line, "end") == 0) {
            continue;
        }
        if (starts_with(line, "field ")) {
            add_field(rt, line);
        } else if (starts_with(line, "module ")) {
            add_module(rt, line);
        } else if (starts_with(line, "cell ")) {
            add_cell(rt, line);
        } else if (starts_with(line, "channel ")) {
            add_channel(rt, line);
        } else if (starts_with(line, "flow ")) {
            add_step(rt, line, STEP_FLOW, "flow ");
        } else if (starts_with(line, "commit ")) {
            add_step(rt, line, STEP_COMMIT, "commit ");
        } else if (starts_with(line, "nest ")) {
            add_step(rt, line, STEP_NEST, "nest ");
        } else if (starts_with(line, "compile ")) {
            add_compile_job(rt, line);
        } else if (starts_with(line, "proof ")) {
            add_proof_job(rt, line);
        } else if (starts_with(line, "council ")) {
            add_council(rt, line);
        } else if (starts_with(line, "deliberate ")) {
            add_deliberation(rt, line);
        } else if (starts_with(line, "evolve ")) {
            add_evolution(rt, line);
        }
    }
    fclose(fp);
}

static void run_flow(Runtime *rt, Step *step) {
    Field *field = find_field(rt, step->field);
    double next_theta[MAX_CELLS];
    Cell *expected;
    if (!field) {
        fail("flow references unknown field");
    }
    for (int i = 0; i < rt->cell_count; i++) {
        next_theta[i] = rt->cells[i].theta;
        if (cell_in_field(rt, &rt->cells[i], field->name)) {
            next_theta[i] += rt->cells[i].omega * step->duration;
        }
    }
    for (int i = 0; i < rt->channel_count; i++) {
        Channel *channel = &rt->channels[i];
        int source_index = find_cell_index(rt, channel->source);
        int target_index = find_cell_index(rt, channel->target);
        Cell *source;
        Cell *target;
        double phase_delta;
        if (source_index < 0 || target_index < 0) {
            fail("flow channel references unknown cell");
        }
        source = &rt->cells[source_index];
        target = &rt->cells[target_index];
        if (!cell_in_field(rt, source, field->name) || !cell_in_field(rt, target, field->name)) {
            continue;
        }
        phase_delta = sin(source->theta + channel->angle - target->theta);
        next_theta[target_index] += field->gain * channel->weight * phase_delta * step->duration;
    }
    for (int i = 0; i < rt->cell_count; i++) {
        if (cell_in_field(rt, &rt->cells[i], field->name)) {
            rt->cells[i].theta = next_theta[i];
        }
    }
    if (step->has_expect_theta) {
        expected = find_cell(rt, step->expect_theta_cell);
        if (!expected) {
            fail("flow expectation references unknown cell");
        }
        if (!close_enough(expected->theta, step->expect_theta, step->tolerance)) {
            fail("flow expectation mismatch");
        }
        printf("flow=%s field=%s duration=%.6f theta %s=%.6f\n",
               step->id, field->name, step->duration, expected->name, expected->theta);
    } else {
        printf("flow=%s field=%s duration=%.6f\n", step->id, field->name, step->duration);
    }
}

static void run_commit(Runtime *rt, Step *step) {
    Module *module = find_module(rt, step->module);
    Field *field;
    char trits[128];
    int trit_count = 0;
    int balance = 0;
    int admissible = 1;
    if (!module) {
        fail("commit references unknown module");
    }
    field = find_field(rt, module->field);
    if (!field) {
        fail("commit module references unknown field");
    }
    for (int i = 0; i < rt->cell_count; i++) {
        Cell *cell = &rt->cells[i];
        char trit;
        int value;
        if (strcmp(cell->module, module->name) != 0) {
            continue;
        }
        trit = trit_from_theta(cell->theta, field->deadband);
        value = trit_value(trit);
        if (balance + value < 0) {
            trit = '0';
            value = 0;
            cell->theta = PI / 2.0;
        }
        balance += value;
        if (balance < 0) {
            admissible = 0;
        }
        cell->latch = trit;
        cell->has_latch = 1;
        if (trit_count + 1 >= (int)sizeof(trits)) {
            fail("commit trit vector too long");
        }
        trits[trit_count++] = trit;
    }
    trits[trit_count] = '\0';
    if (step->expect_trits[0] && strcmp(trits, step->expect_trits) != 0) {
        fail("commit trit expectation mismatch");
    }
    if (strcmp(step->expect_balance, "admissible") == 0 && !admissible) {
        fail("commit balance expectation mismatch");
    }
    printf("commit=%s module=%s trits=%s balance=%s\n",
           step->id, module->name, trits, admissible ? "admissible" : "violated");
}

static double module_mean_trit(Runtime *rt, Module *module) {
    Field *field = find_field(rt, module->field);
    int count = 0;
    double total = 0.0;
    if (!field) {
        fail("module references unknown field");
    }
    for (int i = 0; i < rt->cell_count; i++) {
        Cell *cell = &rt->cells[i];
        char trit;
        if (strcmp(cell->module, module->name) != 0) {
            continue;
        }
        trit = cell->has_latch ? cell->latch : trit_from_theta(cell->theta, field->deadband);
        total += (double)trit_value(trit);
        count++;
    }
    if (count == 0) {
        fail("module has no cells");
    }
    return total / (double)count;
}

static void run_nest(Runtime *rt, Step *step) {
    Module *parent = find_module(rt, step->parent);
    Module *child = find_module(rt, step->child);
    Field *field;
    double up;
    if (!parent || !child) {
        fail("nest references unknown parent or child");
    }
    field = find_field(rt, parent->field);
    if (!field || strcmp(parent->field, child->field) != 0) {
        fail("nest modules must share a field");
    }
    up = module_mean_trit(rt, child);
    parent->belief += field->gain * up;
    child->prior = parent->belief;
    if (step->has_expect_parent_belief &&
        !close_enough(parent->belief, step->expect_parent_belief, step->tolerance)) {
        fail("nest parent belief expectation mismatch");
    }
    if (step->has_expect_child_prior &&
        !close_enough(child->prior, step->expect_child_prior, step->tolerance)) {
        fail("nest child prior expectation mismatch");
    }
    printf("nest=%s parent=%s child=%s up=%.6f parent-belief=%.6f child-prior=%.6f\n",
           step->id, parent->name, child->name, up, parent->belief, child->prior);
}

static void run_steps(Runtime *rt, const char *path) {
    int flow_count = 0;
    int commit_count = 0;
    int nest_count = 0;
    if (rt->step_count == 0) {
        fail("native reducer source has no steps");
    }
    for (int i = 0; i < rt->step_count; i++) {
        Step *step = &rt->steps[i];
        if (step->kind == STEP_FLOW) {
            run_flow(rt, step);
            flow_count++;
        } else if (step->kind == STEP_COMMIT) {
            run_commit(rt, step);
            commit_count++;
        } else if (step->kind == STEP_NEST) {
            run_nest(rt, step);
            nest_count++;
        }
    }
    if (flow_count == 0 || commit_count == 0 || nest_count == 0) {
        fail("native reducer source must exercise flow, commit, and nest");
    }
    printf("native reducer ok steps=%d flow=%d commit=%d nest=%d source=%s\n",
           rt->step_count, flow_count, commit_count, nest_count, path);
}

static void count_step_kinds(Runtime *rt, int *flow_count, int *commit_count, int *nest_count) {
    *flow_count = 0;
    *commit_count = 0;
    *nest_count = 0;
    for (int i = 0; i < rt->step_count; i++) {
        if (rt->steps[i].kind == STEP_FLOW) {
            (*flow_count)++;
        } else if (rt->steps[i].kind == STEP_COMMIT) {
            (*commit_count)++;
        } else if (rt->steps[i].kind == STEP_NEST) {
            (*nest_count)++;
        }
    }
}

static const char *step_kind_name(StepKind kind) {
    if (kind == STEP_FLOW) {
        return "flow";
    }
    if (kind == STEP_COMMIT) {
        return "commit";
    }
    return "nest";
}

static void compile_source(Runtime *rt, const char *path) {
    int flow_count;
    int commit_count;
    int nest_count;
    if (rt->compile_job_count == 0) {
        fail("native reducer source has no compile job");
    }
    count_step_kinds(rt, &flow_count, &commit_count, &nest_count);
    printf("cdc-ir source=%s fields=%d modules=%d cells=%d channels=%d ops=%d\n",
           path, rt->field_count, rt->module_count, rt->cell_count, rt->channel_count, rt->step_count);
    for (int i = 0; i < rt->step_count; i++) {
        Step *step = &rt->steps[i];
        if (step->kind == STEP_FLOW) {
            printf("op[%d]=%s id=%s field=%s duration=%.6f\n",
                   i, step_kind_name(step->kind), step->id, step->field, step->duration);
        } else if (step->kind == STEP_COMMIT) {
            printf("op[%d]=%s id=%s module=%s\n",
                   i, step_kind_name(step->kind), step->id, step->module);
        } else {
            printf("op[%d]=%s id=%s parent=%s child=%s\n",
                   i, step_kind_name(step->kind), step->id, step->parent, step->child);
        }
    }
    for (int i = 0; i < rt->compile_job_count; i++) {
        CompileJob *job = &rt->compile_jobs[i];
        if (job->expect_ops >= 0 && job->expect_ops != rt->step_count) {
            fail("compile job op count mismatch");
        }
        if (job->expect_flow >= 0 && job->expect_flow != flow_count) {
            fail("compile job flow count mismatch");
        }
        if (job->expect_commit >= 0 && job->expect_commit != commit_count) {
            fail("compile job commit count mismatch");
        }
        if (job->expect_nest >= 0 && job->expect_nest != nest_count) {
            fail("compile job nest count mismatch");
        }
        printf("compile-job=%s source=%s ops=%d flow=%d commit=%d nest=%d\n",
               job->id, job->source[0] ? job->source : path, rt->step_count, flow_count, commit_count, nest_count);
    }
    printf("native compile ok jobs=%d ops=%d source=%s\n", rt->compile_job_count, rt->step_count, path);
}

static int pow_int(int base, int exp) {
    int value = 1;
    for (int i = 0; i < exp; i++) {
        value *= base;
    }
    return value;
}

static void check_trit_walk_job(ProofJob *job) {
    int total;
    int admissible = 0;
    int localized = 0;
    int saturated = 0;
    int catalan = 0;
    if (strcmp(job->carrier, "balanced-ternary") != 0) {
        fail("unsupported proof carrier");
    }
    if (job->arity <= 0 || job->arity > 12) {
        fail("proof arity out of supported finite range");
    }
    total = pow_int(3, job->arity);
    for (int code = 0; code < total; code++) {
        int x = code;
        int balance = 0;
        int ok = 1;
        int has_zero = 0;
        for (int i = 0; i < job->arity; i++) {
            int digit = x % 3;
            int trit = digit - 1;
            x /= 3;
            if (trit == 0) {
                has_zero = 1;
            }
            balance += trit;
            if (balance < 0) {
                ok = 0;
                break;
            }
        }
        if (ok) {
            admissible++;
            if (!has_zero) {
                saturated++;
            }
            if (balance == 0) {
                localized++;
                if (!has_zero) {
                    catalan++;
                }
            }
        }
    }
    if (job->expect_total >= 0 && job->expect_total != total) {
        fail("proof total mismatch");
    }
    if (job->expect_admissible >= 0 && job->expect_admissible != admissible) {
        fail("proof admissible count mismatch");
    }
    if (job->expect_localized >= 0 && job->expect_localized != localized) {
        fail("proof localized count mismatch");
    }
    if (job->expect_saturated >= 0 && job->expect_saturated != saturated) {
        fail("proof saturated count mismatch");
    }
    if (job->expect_catalan >= 0 && job->expect_catalan != catalan) {
        fail("proof catalan count mismatch");
    }
    printf("proof=%s carrier=%s arity=%d total=%d admissible=%d localized=%d saturated=%d catalan=%d\n",
           job->id, job->carrier, job->arity, total, admissible, localized, saturated, catalan);
}

static void prove_source(Runtime *rt, const char *path) {
    if (rt->proof_job_count == 0) {
        fail("native reducer source has no proof job");
    }
    for (int i = 0; i < rt->proof_job_count; i++) {
        check_trit_walk_job(&rt->proof_jobs[i]);
    }
    printf("native proof ok jobs=%d source=%s\n", rt->proof_job_count, path);
}

static void interpret_source(Runtime *rt, const char *path) {
    int flow_count = 0;
    int commit_count = 0;
    int nest_count = 0;
    if (rt->step_count == 0) {
        fail("native reducer source has no IR operations");
    }
    printf("ir-interpreter source=%s ops=%d\n", path, rt->step_count);
    for (int i = 0; i < rt->step_count; i++) {
        Step *step = &rt->steps[i];
        printf("ir-exec op[%d]=%s id=%s\n", i, step_kind_name(step->kind), step->id);
        if (step->kind == STEP_FLOW) {
            run_flow(rt, step);
            flow_count++;
        } else if (step->kind == STEP_COMMIT) {
            run_commit(rt, step);
            commit_count++;
        } else if (step->kind == STEP_NEST) {
            run_nest(rt, step);
            nest_count++;
        }
    }
    if (flow_count == 0 || commit_count == 0 || nest_count == 0) {
        fail("IR interpreter must exercise flow, commit, and nest");
    }
    printf("native interpret ok ops=%d flow=%d commit=%d nest=%d source=%s\n",
           rt->step_count, flow_count, commit_count, nest_count, path);
}

static void trits_to_occupancy6(const char *trits, char out[7]) {
    if (strlen(trits) != 6) {
        fail("council bridge coordinate expects six trits");
    }
    for (int i = 0; i < 6; i++) {
        if (trits[i] == '+' || trits[i] == '-') {
            out[i] = '1';
        } else if (trits[i] == '0') {
            out[i] = '0';
        } else {
            fail("council trits must be balanced ternary");
        }
    }
    out[6] = '\0';
}

static void triadic_from_index64(int index, char out[4]) {
    out[0] = (char)('0' + ((index >> 4) & 3));
    out[1] = (char)('0' + ((index >> 2) & 3));
    out[2] = (char)('0' + (index & 3));
    out[3] = '\0';
}

static int dyadic6_to_index(const char *dyadic) {
    int value = 0;
    if (strlen(dyadic) != 6) {
        fail("dyadic bridge coordinate must have six bits");
    }
    for (int i = 0; i < 6; i++) {
        if (dyadic[i] != '0' && dyadic[i] != '1') {
            fail("dyadic bridge coordinate must be binary");
        }
        value = (value << 1) | (dyadic[i] - '0');
    }
    return value;
}

static void append_module_trits(Runtime *rt, Module *module, char *trits, size_t trits_size) {
    Field *field = find_field(rt, module->field);
    size_t used = strlen(trits);
    if (!field) {
        fail("council module references unknown field");
    }
    for (int i = 0; i < rt->cell_count; i++) {
        Cell *cell = &rt->cells[i];
        if (strcmp(cell->module, module->name) != 0) {
            continue;
        }
        if (used + 1 >= trits_size) {
            fail("council trit vector too long");
        }
        trits[used++] = trit_from_theta(cell->theta, field->deadband);
        trits[used] = '\0';
    }
}

static void run_council(Runtime *rt, const char *path) {
    if (rt->deliberation_count == 0) {
        fail("source has no council deliberation");
    }
    for (int i = 0; i < rt->deliberation_count; i++) {
        Deliberation *deliberation = &rt->deliberations[i];
        Council *council = find_council(rt, deliberation->council);
        char members[256];
        char trits[128] = "";
        char dyadic[7];
        char triadic[4];
        char decision[32];
        int occupancy = 0;
        int index;
        char *cursor;
        if (!council) {
            fail("deliberation references unknown council");
        }
        snprintf(members, sizeof(members), "%s", council->members);
        cursor = strtok(members, ",");
        while (cursor) {
            Module *member = find_module(rt, cursor);
            if (!member) {
                fail("council member references unknown module");
            }
            append_module_trits(rt, member, trits, sizeof(trits));
            cursor = strtok(NULL, ",");
        }
        trits_to_occupancy6(trits, dyadic);
        for (int j = 0; j < 6; j++) {
            if (dyadic[j] == '1') {
                occupancy++;
            }
        }
        index = dyadic6_to_index(dyadic);
        triadic_from_index64(index, triadic);
        snprintf(decision, sizeof(decision), "%s", occupancy >= council->quorum ? "adopt" : "hold");
        if (council->expect_decision[0] && strcmp(decision, council->expect_decision) != 0) {
            fail("council decision expectation mismatch");
        }
        if (council->expect_dyadic[0] && strcmp(dyadic, council->expect_dyadic) != 0) {
            fail("council dyadic expectation mismatch");
        }
        if (council->expect_triadic[0] && strcmp(triadic, council->expect_triadic) != 0) {
            fail("council triadic expectation mismatch");
        }
        printf("council=%s deliberation=%s trits=%s dyadic=%s triadic=%s occupancy=%d quorum=%d decision=%s\n",
               council->id, deliberation->id, trits, dyadic, triadic, occupancy, council->quorum, decision);
    }
    printf("native council ok deliberations=%d source=%s\n", rt->deliberation_count, path);
}

static int file_contains(const char *path, const char *needle) {
    FILE *fp = fopen(path, "r");
    char line[LINE_MAX_BYTES];
    if (!fp) {
        return 0;
    }
    while (fgets(line, sizeof(line), fp)) {
        if (strstr(line, needle)) {
            fclose(fp);
            return 1;
        }
    }
    fclose(fp);
    return 0;
}

static void run_evolution(Runtime *rt, const char *path) {
    if (rt->evolution_count == 0) {
        fail("source has no evolution job");
    }
    for (int i = 0; i < rt->evolution_count; i++) {
        EvolutionJob *job = &rt->evolutions[i];
        FILE *in = fopen(job->source, "r");
        FILE *out;
        char line[LINE_MAX_BYTES];
        if (!in) {
            fail("evolution source could not be opened");
        }
        out = fopen(job->output, "w");
        if (!out) {
            fclose(in);
            fail("evolution output could not be opened");
        }
        while (fgets(line, sizeof(line), in)) {
            fputs(line, out);
        }
        fprintf(out, "\n# evolved by bridge coordinate %s through %s\n", job->coordinate, job->id);
        fprintf(out, "witness %s invariant=dyadic-triadic-closure coordinate=%s claim=\"bridge coordinate self evolution wrote this witness\"\n",
                job->append_witness, job->coordinate);
        fclose(in);
        fclose(out);
        if (job->expect_contains[0] && !file_contains(job->output, job->expect_contains)) {
            fail("evolution output missing expected text");
        }
        printf("evolution=%s coordinate=%s source=%s output=%s appended=%s\n",
               job->id, job->coordinate, job->source, job->output, job->append_witness);
    }
    printf("native evolution ok jobs=%d source=%s\n", rt->evolution_count, path);
}

static void usage(void) {
    fprintf(stderr, "usage:\n");
    fprintf(stderr, "  cdc_native_runtime run native_reducer.cdc\n");
    fprintf(stderr, "  cdc_native_runtime compile native_reducer.cdc\n");
    fprintf(stderr, "  cdc_native_runtime interpret native_reducer.cdc\n");
    fprintf(stderr, "  cdc_native_runtime prove native_reducer.cdc\n");
    fprintf(stderr, "  cdc_native_runtime council council_bridge.cdc\n");
    fprintf(stderr, "  cdc_native_runtime evolve council_bridge.cdc\n");
    exit(2);
}

int main(int argc, char **argv) {
    Runtime runtime;
    if (argc != 3) {
        usage();
    }
    parse_source(&runtime, argv[2]);
    if (strcmp(argv[1], "run") == 0) {
        run_steps(&runtime, argv[2]);
    } else if (strcmp(argv[1], "compile") == 0) {
        compile_source(&runtime, argv[2]);
    } else if (strcmp(argv[1], "interpret") == 0) {
        interpret_source(&runtime, argv[2]);
    } else if (strcmp(argv[1], "prove") == 0) {
        prove_source(&runtime, argv[2]);
    } else if (strcmp(argv[1], "council") == 0) {
        run_council(&runtime, argv[2]);
    } else if (strcmp(argv[1], "evolve") == 0) {
        run_evolution(&runtime, argv[2]);
    } else {
        usage();
    }
    return 0;
}
