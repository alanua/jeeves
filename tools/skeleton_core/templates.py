"""Runner issue rendering for Skeleton task packets."""

from textwrap import dedent

from tools.skeleton_core.models import RouteDecision, RouteTarget, TaskPacket

REQUIRED_RUNNER_REPORT_SHAPE = """changed_files
commands_run
test_result
lint_result
format_result
diff_summary
errors_or_blockers
private_data_seen: yes/no
runtime_code_touched: yes/no
external_services_called: yes/no
next_safe_step"""

SAFETY_BOUNDARIES = """- new code must live outside the Jeeves runtime app package when applicable
- do not modify Jeeves runtime behavior
- no Gemini / NotebookLM / Antigravity calls
- no GitHub / Drive / Gmail / external API calls from the implementation
- no secrets, .env, OAuth, SSH, deploy, infra, DB migrations, or production access
- no private infrastructure details in reports"""


def render_runner_issue(packet: TaskPacket, decision: RouteDecision) -> str:
    """Render a bounded runner issue body for a Skeleton task."""
    blocked_section = ""
    if decision.route_target == RouteTarget.BLOCKED_RED:
        blocked_section = dedent(
            f"""
            ## Blocked

            This task is blocked and not executable.

            Reason:

            ```text
            {decision.blocked_reason}
            ```
            """
        ).strip()

    body = dedent(
        f"""
        # [skeleton-task] {packet.title}

        ## Active project

        ```text
        СК / ChatGPT Exoskeleton
        ```

        ## Project

        ```text
        {packet.project}
        ```

        ## Risk level

        ```text
        {decision.risk_level}
        ```

        ## Route target

        ```text
        {decision.route_target}
        ```

        ## Evidence policy

        ```text
        {decision.evidence_policy}
        ```

        Evidence is never canon by default. This task packet records evidence policy only; it does not authorize external service calls.

        ## Original task body

        ```text
        {packet.body}
        ```

        {blocked_section}

        ## Safety boundaries

        ```text
        {SAFETY_BOUNDARIES}
        ```

        ## Expected output

        Return a short public-safe runner report. Do not include secrets, private infrastructure details, or raw private material.

        ## Required runner report shape

        ```text
        {REQUIRED_RUNNER_REPORT_SHAPE}
        ```
        """
    ).strip()

    return body + "\n"
