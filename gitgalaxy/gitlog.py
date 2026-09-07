import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Commit:
    sha: str
    author: str
    email: str
    timestamp: datetime
    message: str
    insertions: int
    deletions: int

    @property
    def churn(self) -> int:
        return self.insertions + self.deletions


class NotAGitRepoError(Exception):
    pass


class EmptyRepoError(Exception):
    pass


def _run(args, cwd):
    try:
        result = subprocess.run(
            args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
    except FileNotFoundError as e:
        raise NotAGitRepoError(f"path not found: {cwd}") from e
    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "does not have any commits yet" in stderr:
            raise EmptyRepoError("this repository has no commits yet")
        raise NotAGitRepoError(stderr or "git command failed")
    return result.stdout


def is_git_repo(path: str) -> bool:
    try:
        out = _run(["git", "rev-parse", "--is-inside-work-tree"], cwd=path)
        return out.strip() == "true"
    except NotAGitRepoError:
        return False


SEP = "\x1f"
REC_SEP = "\x1e"


def load_commits(path: str, days: int = None, limit: int = None, branch: str = None):
    if not is_git_repo(path):
        raise NotAGitRepoError(f"'{path}' is not a git repository")

    fmt = f"{REC_SEP}%H{SEP}%an{SEP}%ae{SEP}%at{SEP}%s"
    args = ["git", "log", f"--pretty=format:{fmt}", "--numstat"]
    if days:
        args.append(f"--since={days}.days")
    if limit:
        args.append(f"-n{limit}")
    if branch:
        args.append(branch)

    try:
        raw = _run(args, cwd=path)
    except EmptyRepoError:
        return []
    commits = []

    for record in raw.split(REC_SEP):
        record = record.strip("\n")
        if not record.strip():
            continue
        lines = record.split("\n")
        header = lines[0]
        parts = header.split(SEP)
        if len(parts) < 5:
            continue
        sha, author, email, ts, message = parts[0], parts[1], parts[2], parts[3], parts[4]

        insertions = 0
        deletions = 0
        for stat_line in lines[1:]:
            stat_line = stat_line.strip()
            if not stat_line:
                continue
            cols = stat_line.split("\t")
            if len(cols) < 3:
                continue
            ins, dele = cols[0], cols[1]
            if ins.isdigit():
                insertions += int(ins)
            if dele.isdigit():
                deletions += int(dele)

        try:
            timestamp = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        except ValueError:
            continue

        commits.append(
            Commit(
                sha=sha,
                author=author.strip(),
                email=email.strip(),
                timestamp=timestamp,
                message=message.strip(),
                insertions=insertions,
                deletions=deletions,
            )
        )

    commits.sort(key=lambda c: c.timestamp)
    return commits
