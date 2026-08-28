# TODO (authoring-time placeholder): pin this to whatever base image the
# template fork's other CFD examples use (see
# examples/openfoam-hydrofoil-flap/environment/Dockerfile for the
# established pattern) so the OpenFOAM version matches what produced the
# reference numbers. This case was built/run against OpenFOAM v2606
# (`source /usr/lib/openfoam/openfoam2606/etc/bashrc`).
FROM opencfd/openfoam-run:2606

RUN useradd -m -u 1000 -s /bin/bash agent

WORKDIR /workdir
RUN mkdir -p /tmp/output && chown -R agent:agent /workdir /tmp/output

# Public contract: mesh, case dicts, BCs, and the SCRIPTS/ pipeline the
# agent runs to mesh + solve. scorer/ and scorer/data/ are NOT copied here
# so the agent image never has access to the hidden reference values.
COPY data/ /workdir/data/
COPY --chown=agent:agent SCRIPTS/ /workdir/SCRIPTS/
RUN chown -R agent:agent /workdir/data

USER agent
ENV OPENFOAM_BASHRC=/usr/lib/openfoam/openfoam2606/etc/bashrc
SHELL ["/bin/bash", "-c"]
