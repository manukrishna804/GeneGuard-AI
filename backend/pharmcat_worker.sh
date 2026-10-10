#!/bin/bash

set -u

JOBS_DIR="/data/jobs"
mkdir -p "$JOBS_DIR"

echo "GeneGuard PharmCAT worker started"

while true; do
    for job_dir in "$JOBS_DIR"/*; do
        [ -d "$job_dir" ] || continue
        [ -f "$job_dir/ready" ] || continue

        # Claim the job to avoid processing it twice.
        mv "$job_dir/ready" "$job_dir/processing" 2>/dev/null || continue

        echo "Processing job: $(basename "$job_dir")"

        mkdir -p "$job_dir/output"

        if pharmcat_pipeline \
            -o "$job_dir/output" \
            -reporterJson "$job_dir/input.vcf" \
            > "$job_dir/stdout.log" \
            2> "$job_dir/stderr.log"
        then
            echo "success" > "$job_dir/status.tmp"
        else
            echo "error" > "$job_dir/status.tmp"
        fi

        mv "$job_dir/status.tmp" "$job_dir/status"
        rm -f "$job_dir/processing"

        echo "Finished job: $(basename "$job_dir")"
    done

    sleep 1
done