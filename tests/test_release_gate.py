#!/usr/bin/env python3
"""Characterization tests for the read-only release gate."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GATE = REPO_ROOT / "release-gate"
MANIFEST = REPO_ROOT / "release-manifest.json"

EXPECTED_RUNTIME_FIXTURE_BLOCKERS = {
    "VERSION_DRIFT",
    "RUNTIME_POLICY_FALSE",
}


def run_gate(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_gate_json(*args: str) -> tuple[subprocess.CompletedProcess[str], dict]:
    with tempfile.TemporaryDirectory(prefix="short-drama-gate-test-") as tmp:
        out = Path(tmp) / "report.json"
        result = run_gate(*args, "--json-out", str(out))
        report = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    return result, report


def write_manifest(path: Path, manifest: dict) -> Path:
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def run_cmd(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)


class ReleaseGateTests(unittest.TestCase):
    def load_real_manifest(self) -> dict:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))

    def check_ids(self, report: dict) -> set[str]:
        return set(report["summary"]["checks_failed"])

    def write_local_smoke_repo(self, tmp_path: Path) -> Path:
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / "install.sh").write_text((REPO_ROOT / "install.sh").read_text(encoding="utf-8"), encoding="utf-8")
        for package in ("short-drama", "short-drama-remake"):
            package_root = repo / package
            package_root.mkdir()
            (package_root / "SKILL.md").write_text(
                f"---\nname: {package}\ndescription: fixture\n---\n",
                encoding="utf-8",
            )
            (package_root / "VERSION").write_text("9.9.9\n", encoding="utf-8")
        manifest = self.load_real_manifest()
        manifest["canonical_repo"]["path"] = str(repo)
        manifest["canonical_repo"]["remote"] = "https://github.com/MarkQWu/drama-workshop-skills.git"
        manifest["canonical_repo"]["repo_name"] = "drama-workshop-skills"
        manifest["package_root"] = "short-drama"
        manifest["distribution_repo"]["package_roots"] = ["short-drama", "short-drama-remake"]
        manifest["distribution_repo"]["installers"] = ["install.sh"]
        manifest["runtime_roots"] = [
            {
                "name": "claude",
                "path": "~/.claude/skills/short-drama",
                "policy": "generated_copy",
                "required": True,
            },
            {
                "name": "codex",
                "path": "~/.codex/skills/short-drama",
                "policy": "generated_copy",
                "required": True,
            },
        ]
        manifest["sibling_skills"] = []
        write_manifest(repo / "release-manifest.json", manifest)

        self.assertEqual(run_cmd(["git", "init"], repo).returncode, 0)
        self.assertEqual(run_cmd(["git", "add", "."], repo).returncode, 0)
        commit = run_cmd(
            [
                "git",
                "-c",
                "user.email=fixture@example.invalid",
                "-c",
                "user.name=Fixture",
                "commit",
                "-m",
                "fixture",
            ],
            repo,
        )
        self.assertEqual(commit.returncode, 0, commit.stderr)
        return repo

    def write_runtime_drift_fixture_manifest(self, tmp_path: Path) -> Path:
        runtime_parent = tmp_path / "runtime"
        runtime_root = runtime_parent / "short-drama"
        runtime_root.mkdir(parents=True)
        (runtime_root / "VERSION").write_text("0.0.1\n", encoding="utf-8")
        (runtime_root / "WHATSNEW.md").write_text("**v0.0.1**\n", encoding="utf-8")
        (runtime_parent / "short-drama-remake").mkdir()
        distribution_package = tmp_path / "short-drama"
        distribution_package.mkdir()
        (distribution_package / "SKILL.md").write_text(
            "---\nname: short-drama\ndescription: fixture\n---\n",
            encoding="utf-8",
        )
        sibling_package = tmp_path / "short-drama-remake"
        sibling_package.mkdir()
        (sibling_package / "SKILL.md").write_text(
            "---\nname: short-drama-remake\ndescription: fixture\n---\n",
            encoding="utf-8",
        )

        manifest = self.load_real_manifest()
        manifest["package_root"] = str(REPO_ROOT / "short-drama")
        manifest["distribution_repo"]["installers"] = []
        manifest["runtime_roots"] = [
            {
                "name": "fixture-runtime",
                "path": str(runtime_root),
                "policy": "generated_copy",
                "required": True,
            }
        ]
        return write_manifest(tmp_path / "release-manifest.json", manifest)

    def test_fixture_full_dry_run_fails_expected_runtime_blockers(self) -> None:
        with tempfile.TemporaryDirectory(prefix="short-drama-gate-runtime-") as tmp:
            manifest_path = self.write_runtime_drift_fixture_manifest(Path(tmp))
            result, report = run_gate_json("--dry-run", "--manifest", str(manifest_path))

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(report["status"], "fail")
        self.assertEqual(self.check_ids(report), EXPECTED_RUNTIME_FIXTURE_BLOCKERS)

    def test_check_version_drift_returns_only_version_drift(self) -> None:
        with tempfile.TemporaryDirectory(prefix="short-drama-gate-runtime-") as tmp:
            manifest_path = self.write_runtime_drift_fixture_manifest(Path(tmp))
            result, report = run_gate_json(
                "--dry-run",
                "--manifest",
                str(manifest_path),
                "--check",
                "VERSION_DRIFT",
            )

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.check_ids(report), {"VERSION_DRIFT"})

    def test_check_runtime_policy_false_returns_only_runtime_policy_false(self) -> None:
        with tempfile.TemporaryDirectory(prefix="short-drama-gate-runtime-") as tmp:
            manifest_path = self.write_runtime_drift_fixture_manifest(Path(tmp))
            result, report = run_gate_json(
                "--dry-run",
                "--manifest",
                str(manifest_path),
                "--check",
                "RUNTIME_POLICY_FALSE",
            )

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.check_ids(report), {"RUNTIME_POLICY_FALSE"})

    def test_sibling_runtime_drift_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory(prefix="short-drama-gate-sibling-runtime-") as tmp:
            tmp_path = Path(tmp)
            for package, version in (("short-drama", "1.0.0"), ("short-drama-remake", "2.0.0")):
                package_root = tmp_path / package
                package_root.mkdir()
                (package_root / "SKILL.md").write_text(
                    f"---\nname: {package}\ndescription: fixture\n---\n",
                    encoding="utf-8",
                )
                (package_root / "VERSION").write_text(f"{version}\n", encoding="utf-8")

            runtime_parent = tmp_path / "runtime"
            for package, version in (("short-drama", "1.0.0"), ("short-drama-remake", "0.1.0")):
                runtime_root = runtime_parent / package
                runtime_root.mkdir(parents=True)
                (runtime_root / "SKILL.md").write_text(
                    f"---\nname: {package}\ndescription: fixture\n---\n",
                    encoding="utf-8",
                )
                (runtime_root / "VERSION").write_text(f"{version}\n", encoding="utf-8")

            manifest = self.load_real_manifest()
            manifest["package_root"] = "short-drama"
            manifest["distribution_repo"]["package_roots"] = ["short-drama", "short-drama-remake"]
            manifest["distribution_repo"]["installers"] = []
            manifest["runtime_roots"] = [
                {
                    "name": "fixture-runtime",
                    "path": str(runtime_parent / "short-drama"),
                    "policy": "generated_copy",
                    "required": True,
                }
            ]
            manifest_path = write_manifest(tmp_path / "release-manifest.json", manifest)

            result, report = run_gate_json(
                "--dry-run",
                "--manifest",
                str(manifest_path),
                "--check",
                "RUNTIME_POLICY_FALSE",
            )

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.check_ids(report), {"RUNTIME_POLICY_FALSE"})
        self.assertIn("fixture-runtime:short-drama-remake", json.dumps(report, ensure_ascii=False))

    def test_canonical_symlink_policy_rejects_real_runtime_directory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="short-drama-gate-canonical-symlink-") as tmp:
            tmp_path = Path(tmp)
            package = tmp_path / "short-drama"
            runtime = tmp_path / "runtime" / "short-drama"
            for root in (package, runtime):
                root.mkdir(parents=True)
                (root / "SKILL.md").write_text(
                    "---\nname: short-drama\ndescription: fixture\n---\n",
                    encoding="utf-8",
                )
                (root / "VERSION").write_text("1.0.0\n", encoding="utf-8")

            manifest = self.load_real_manifest()
            manifest["package_root"] = str(package)
            manifest["distribution_repo"]["package_roots"] = ["short-drama"]
            manifest["distribution_repo"]["installers"] = []
            manifest["runtime_roots"] = [
                {
                    "name": "fixture-runtime",
                    "path": str(runtime),
                    "policy": "canonical_symlink",
                    "required": True,
                }
            ]
            manifest["sibling_skills"] = []
            manifest_path = write_manifest(tmp_path / "release-manifest.json", manifest)

            result, report = run_gate_json(
                "--dry-run",
                "--manifest",
                str(manifest_path),
                "--check",
                "RUNTIME_POLICY_FALSE",
            )

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.check_ids(report), {"RUNTIME_POLICY_FALSE"})
        self.assertIn("not-canonical-symlink", json.dumps(report, ensure_ascii=False))

    def test_package_surface_scope_checks_pass_current_package(self) -> None:
        for check_id in (
            "FRONTMATTER_PARSE",
            "HELP_SOURCE_MATCH",
            "DUPLICATE_AUTHORITY_DOCS",
            "DUPLICATE_AUTHORITY_SCRIPTS",
            "UPDATE_POLICY_REPO_NAME",
            "UPDATE_CHECK_SPLIT",
            "INSTALLER_CONTRACT",
            "UPDATE_REPO_NAME_DRIFT",
            "SKILL_DISCOVERY",
        ):
            with self.subTest(check_id=check_id):
                result, report = run_gate_json("--dry-run", "--check", check_id)

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(report["status"], "pass")
                self.assertEqual(self.check_ids(report), set())

    def test_invalid_frontmatter_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory(prefix="short-drama-gate-frontmatter-") as tmp:
            tmp_path = Path(tmp)
            package = tmp_path / "short-drama"
            package.mkdir()
            (package / "SKILL.md").write_text(
                '---\nname: short-drama\ndescription: "bad "quote" scalar"\n---\n',
                encoding="utf-8",
            )
            manifest = self.load_real_manifest()
            manifest["package_root"] = str(package)
            manifest["distribution_repo"]["package_roots"] = ["short-drama"]
            manifest["runtime_roots"] = []
            manifest["sibling_skills"] = []
            manifest_path = write_manifest(tmp_path / "release-manifest.json", manifest)

            result, report = run_gate_json(
                "--dry-run",
                "--manifest",
                str(manifest_path),
                "--check",
                "FRONTMATTER_PARSE",
            )

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.check_ids(report), {"FRONTMATTER_PARSE"})

    def test_missing_installer_contract_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory(prefix="short-drama-gate-installer-") as tmp:
            tmp_path = Path(tmp)
            package = tmp_path / "short-drama"
            package.mkdir()
            (package / "SKILL.md").write_text(
                "---\nname: short-drama\ndescription: fixture\n---\n",
                encoding="utf-8",
            )
            (tmp_path / "install.sh").write_text("#!/usr/bin/env bash\necho bad\n", encoding="utf-8")
            manifest = self.load_real_manifest()
            manifest["package_root"] = str(package)
            manifest["distribution_repo"]["package_roots"] = ["short-drama"]
            manifest["distribution_repo"]["installers"] = ["install.sh"]
            manifest["runtime_roots"] = []
            manifest["sibling_skills"] = []
            manifest_path = write_manifest(tmp_path / "release-manifest.json", manifest)

            result, report = run_gate_json(
                "--dry-run",
                "--manifest",
                str(manifest_path),
                "--check",
                "INSTALLER_CONTRACT",
            )

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.check_ids(report), {"INSTALLER_CONTRACT"})

    def test_installer_contract_targets_follow_manifest_runtime_roots(self) -> None:
        with tempfile.TemporaryDirectory(prefix="short-drama-gate-installer-targets-") as tmp:
            tmp_path = Path(tmp)
            package = tmp_path / "short-drama"
            package.mkdir()
            (package / "SKILL.md").write_text(
                "---\nname: short-drama\ndescription: fixture\n---\n",
                encoding="utf-8",
            )
            (tmp_path / "install.sh").write_text(
                "#!/usr/bin/env bash\n"
                "REPO_GITHUB='https://github.com/MarkQWu/drama-workshop-skills.git'\n"
                "CACHE=\"$HOME/.alpha/.skill-repos/drama-workshop-skills\"\n"
                "# .skill-trash .trash SKILL.md short-drama/VERSION\n"
                "for d in \"$CACHE\"/*/; do echo \"$HOME/.alpha\"; done\n",
                encoding="utf-8",
            )
            (tmp_path / "install.ps1").write_text(
                "$repoGitHub = 'https://github.com/MarkQWu/drama-workshop-skills.git'\n"
                "$cache = '.alpha'\n"
                "# .skill-trash .trash SKILL.md short-drama\\VERSION\n"
                'Get-ChildItem "$cache" -Directory | ForEach-Object { ".alpha" }\n',
                encoding="utf-8",
            )
            manifest = self.load_real_manifest()
            manifest["package_root"] = str(package)
            manifest["distribution_repo"]["package_roots"] = ["short-drama"]
            manifest["distribution_repo"]["installers"] = ["install.sh", "install.ps1"]
            manifest["runtime_roots"] = [
                {
                    "name": "alpha",
                    "path": "~/.alpha/skills/short-drama",
                    "policy": "generated_copy",
                    "required": True,
                },
                {
                    "name": "beta",
                    "path": "~/.beta/skills/short-drama",
                    "policy": "generated_copy",
                    "required": True,
                },
            ]
            manifest["sibling_skills"] = []
            manifest_path = write_manifest(tmp_path / "release-manifest.json", manifest)

            result, report = run_gate_json(
                "--dry-run",
                "--manifest",
                str(manifest_path),
                "--check",
                "INSTALLER_CONTRACT",
            )

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.check_ids(report), {"INSTALLER_CONTRACT"})
        self.assertIn(".beta", json.dumps(report, ensure_ascii=False))

    def test_installer_local_smoke_passes_in_temp_home(self) -> None:
        with tempfile.TemporaryDirectory(prefix="short-drama-gate-local-smoke-") as tmp:
            repo = self.write_local_smoke_repo(Path(tmp))
            result, report = run_gate_json(
                "--dry-run",
                "--manifest",
                str(repo / "release-manifest.json"),
                "--check",
                "INSTALLER_LOCAL_SMOKE",
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(self.check_ids(report), set())

    def test_installer_local_smoke_requires_clean_worktree(self) -> None:
        with tempfile.TemporaryDirectory(prefix="short-drama-gate-local-smoke-dirty-") as tmp:
            repo = self.write_local_smoke_repo(Path(tmp))
            (repo / "UNCOMMITTED.md").write_text("dirty\n", encoding="utf-8")
            result, report = run_gate_json(
                "--dry-run",
                "--manifest",
                str(repo / "release-manifest.json"),
                "--check",
                "INSTALLER_LOCAL_SMOKE",
            )

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.check_ids(report), {"INSTALLER_LOCAL_SMOKE"})
        self.assertIn("commit or clean worktree", json.dumps(report, ensure_ascii=False))

    def test_excluded_policy_manifest_passes_runtime_policy_check(self) -> None:
        with tempfile.TemporaryDirectory(prefix="short-drama-gate-excluded-") as tmp:
            tmp_path = Path(tmp)
            manifest = self.load_real_manifest()
            manifest["runtime_roots"] = [
                {
                    "name": item["name"],
                    "path": item["path"],
                    "policy": "intentionally excluded by manifest",
                    "required": item.get("required", True),
                }
                for item in manifest["runtime_roots"]
            ]
            manifest_path = write_manifest(tmp_path / "release-manifest.json", manifest)

            result, report = run_gate_json(
                "--dry-run",
                "--manifest",
                str(manifest_path),
                "--check",
                "RUNTIME_POLICY_FALSE",
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(self.check_ids(report), set())

    def test_declared_symlink_manifest_passes_runtime_policy_check(self) -> None:
        with tempfile.TemporaryDirectory(prefix="short-drama-gate-symlink-") as tmp:
            tmp_path = Path(tmp)
            target = tmp_path / "target-runtime"
            target.mkdir()
            link = tmp_path / "runtime-link"
            link.symlink_to(target, target_is_directory=True)

            manifest = self.load_real_manifest()
            manifest["package_root"] = "package"
            manifest["runtime_roots"] = [
                {
                    "name": "declared-symlink",
                    "path": str(link),
                    "target": str(target),
                    "policy": "declared symlink",
                    "required": True,
                }
            ]
            manifest_path = write_manifest(tmp_path / "release-manifest.json", manifest)

            result, report = run_gate_json(
                "--dry-run",
                "--manifest",
                str(manifest_path),
                "--check",
                "RUNTIME_POLICY_FALSE",
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(self.check_ids(report), set())

    def test_unknown_check_id_exits_one(self) -> None:
        result = run_gate("--dry-run", "--check", "NO_SUCH_CHECK")

        self.assertEqual(result.returncode, 1)
        self.assertIn("Unknown check id(s): NO_SUCH_CHECK", result.stderr)


if __name__ == "__main__":
    unittest.main()
