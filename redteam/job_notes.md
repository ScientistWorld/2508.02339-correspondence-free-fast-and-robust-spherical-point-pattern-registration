# Execution notes

The first bundled CPU job, 07b06731-204, completed reference seeds 0/1/2
and the exact faster FFT variant. It checkpointed 32 of 35 configurations for
the finer-resolution variant. The first worker was preempted for SLURM drain;
the second worker then died. With no further progress for about 40 minutes,
the job was cancelled. There was no numerical or method failure in these logs.

The resumed bundle preserves completed case results, runs the fast artifact
checks first, and resumes partial numerical benchmarks. A persistent input-file
backup restores ordinary workspace files if a worker dies during a case.

The second CPU job, 1141bd20-aac, finished with exit code 0. It was preempted
once and resumed automatically; checkpoints preserved all work. All 19 cases
completed, including the two deliberately invalid artifacts whose evaluator
exits were nonzero. Every real numerical variant used all original core cases
and all five point-count scales. Only documentation and stdlib aggregation
were performed on the interactive node.
