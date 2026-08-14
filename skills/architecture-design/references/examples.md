# Architecture calibration

For a notification subsystem, compare direct channel integration with a dispatcher plus queue. Select added infrastructure only when confirmed reliability, throughput, and ownership justify it. Define dispatcher, channel adapters, preference truth owner, data flow, failure modes, and interfaces. Record queue and adapter decisions as separate Proposed ADR artifacts when costly to reverse; retain unsupported retry/degradation choices as blocking assumptions. Recommend design review before planning when ownership or contracts remain uncertain.
