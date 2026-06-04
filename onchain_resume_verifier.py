# CONTRACT 2 — On-Chain Resume Verifier
# Use-case: Fetches a GitHub profile and LinkedIn URL, then uses LLM to verify
# whether a candidate meets stated job requirements.
# =============================================================================
 
# { "Depends": "py-genlayer:latest" }
from genlayer import *
import json
 
class ResumeVerifier(gl.Contract):
    job_title: str
    requirements: str
    evaluations: TreeMap[str, str]
 
    def __init__(self, job_title: str, requirements: str):
        self.job_title = job_title
        self.requirements = requirements
 
    @gl.public.write
    def evaluate_candidate(self, github_username: str, candidate_summary: str) -> dict:
        """
        Fetches GitHub profile data and uses LLM to check if candidate qualifies.
        """
        def nondet() -> str:
            response = gl.nondet.web.get(f"https://api.github.com/users/{github_username}")
            gh_data = response.body.decode("utf-8")
 
            prompt = (
                f"Job: {self.job_title}\n"
                f"Requirements: {self.requirements}\n\n"
                f"Candidate self-summary: {candidate_summary}\n"
                f"GitHub profile data: {gh_data[:2000]}\n\n"
                "Assess if this candidate meets the job requirements.\n"
                'Respond ONLY with JSON:\n'
                '{"qualified": true|false, "score": int(0-100), "strengths": [str], "gaps": [str], "verdict": str}\n'
                'No markdown.'
            )
            result = gl.nondet.exec_prompt(prompt)
            return result
 
        raw = gl.eq_principle.strict_eq(nondet)
        result = json.loads(raw)
        self.evaluations[github_username] = json.dumps(result)
        return result
 
    @gl.public.view
    def get_evaluation(self, github_username: str) -> dict:
        if github_username not in self.evaluations:
            return {}
        return json.loads(self.evaluations[github_username])
 
