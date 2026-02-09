#!/usr/bin/env python3
"""
Quick test for state secrets scanning patterns.
Validates that scan_state_for_secrets() detects known secret patterns
and correctly ignores false positives.

Usage: python3 tests/test_state_scan.py
"""

import sys
import os

# Add scripts directory to path so we can import the functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

# We need to set dummy env vars before importing (the module reads them at import time)
os.environ.setdefault("TFC_TOKEN", "test-token")
os.environ.setdefault("TFC_ORG", "test-org")

from collect_tfc_data import scan_state_for_secrets

# ----- Mock State Data -----

MOCK_STATE_WITH_SECRETS = {
    "version": 4,
    "terraform_version": "1.9.6",
    "resources": [
        {
            "mode": "managed",
            "type": "aws_iam_access_key",
            "name": "deploy",
            "instances": [
                {
                    "attributes": {
                        "id": "AKIAIOSFODNN7EXAMPLE",
                        "secret": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                        "user": "deploy-user",
                        "status": "Active",
                    }
                }
            ],
        },
        {
            "mode": "managed",
            "type": "aws_db_instance",
            "name": "main",
            "instances": [
                {
                    "attributes": {
                        "id": "mydb",
                        "engine": "mysql",
                        "password": "SuperSecret123!",
                        "username": "admin",
                        "endpoint": "mysql://admin:SuperSecret123!@mydb.us-east-1.rds.amazonaws.com:3306/mydb",
                    }
                }
            ],
        },
        {
            "mode": "managed",
            "type": "tls_private_key",
            "name": "example",
            "instances": [
                {
                    "attributes": {
                        "algorithm": "RSA",
                        "private_key_pem": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----",
                        "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...\n-----END PUBLIC KEY-----",
                    }
                }
            ],
        },
        {
            "mode": "managed",
            "type": "github_actions_secret",
            "name": "deploy_token",
            "instances": [
                {
                    "attributes": {
                        "secret_name": "DEPLOY_TOKEN",
                        "plaintext_value": "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijkl",
                    }
                }
            ],
        },
        {
            "mode": "managed",
            "type": "slack_conversation",
            "name": "alerts",
            "instances": [
                {
                    "attributes": {
                        "token": "xoxb-1234567890-1234567890123-ABCDEFGHIJKLMNOPQRSTUVWXYZa",
                        "name": "alerts-channel",
                    }
                }
            ],
        },
    ],
    "outputs": {
        "api_endpoint": {"value": "https://api.example.com", "type": "string"},
        "db_connection": {
            "value": "postgres://user:p4ssw0rd@db.example.com:5432/mydb",
            "type": "string",
        },
    },
}

MOCK_STATE_CLEAN = {
    "version": 4,
    "terraform_version": "1.9.6",
    "resources": [
        {
            "mode": "managed",
            "type": "aws_s3_bucket",
            "name": "logs",
            "instances": [
                {
                    "attributes": {
                        "id": "my-log-bucket",
                        "bucket": "my-log-bucket",
                        "region": "us-east-1",
                        "acl": "private",
                        "tags": {"Environment": "production"},
                    }
                }
            ],
        },
        {
            "mode": "managed",
            "type": "aws_instance",
            "name": "web",
            "instances": [
                {
                    "attributes": {
                        "ami": "ami-0c55b159cbfafe1f0",
                        "instance_type": "t3.micro",
                        "availability_zone": "us-east-1a",
                    }
                }
            ],
        },
    ],
    "outputs": {
        "bucket_name": {"value": "my-log-bucket", "type": "string"},
    },
}

MOCK_STATE_REDACTED = {
    "version": 4,
    "resources": [
        {
            "mode": "managed",
            "type": "aws_db_instance",
            "name": "main",
            "instances": [
                {
                    "attributes": {
                        "password": "(sensitive value)",
                        "username": "admin",
                    }
                }
            ],
        }
    ],
}


# ----- Tests -----


def test_detects_secrets():
    """State with known secrets should produce findings."""
    findings = scan_state_for_secrets(MOCK_STATE_WITH_SECRETS)
    assert len(findings) > 0, "Expected findings but got none"

    patterns_found = {f["pattern"] for f in findings}
    paths_found = {f["attribute_path"] for f in findings}

    # AWS access key (AKIA pattern)
    assert "AWS Access Key" in patterns_found, (
        f"Missing AWS Access Key detection. Found: {patterns_found}"
    )

    # Sensitive attribute name: 'secret' on iam_access_key
    assert any(
        "secret" in f["attribute_path"] and f["pattern"] == "Sensitive attribute name"
        for f in findings
    ), "Missing sensitive attribute 'secret' detection"

    # Sensitive attribute name: 'password' on db_instance
    assert any("password" in f["attribute_path"] for f in findings), (
        "Missing password detection"
    )

    # Private key block
    assert "Private Key Block" in patterns_found, (
        f"Missing Private Key detection. Found: {patterns_found}"
    )

    # GitHub token
    assert "GitHub Token" in patterns_found, (
        f"Missing GitHub Token detection. Found: {patterns_found}"
    )

    # Slack token
    assert "Slack Token" in patterns_found, (
        f"Missing Slack Token detection. Found: {patterns_found}"
    )

    # Connection string in output
    assert any("output.db_connection" in f["attribute_path"] for f in findings), (
        "Missing connection string in output detection"
    )

    # Connection string in resource attribute (endpoint)
    assert "Connection String with Credentials" in patterns_found, (
        f"Missing Connection String detection. Found: {patterns_found}"
    )

    # Sensitive attribute: 'token' on slack_conversation
    assert any(
        f["attribute_path"] == "managed.slack_conversation.alerts.token"
        and f["pattern"] == "Sensitive attribute name"
        for f in findings
    ), "Missing sensitive attribute 'token' detection on slack resource"

    print(
        f"  ✅ Detected {len(findings)} findings across {len(patterns_found)} pattern types"
    )
    for f in findings:
        print(f"     - [{f['pattern']}] {f['attribute_path']}")
    return True


def test_clean_state_no_findings():
    """State with no secrets should produce zero findings."""
    findings = scan_state_for_secrets(MOCK_STATE_CLEAN)
    assert len(findings) == 0, (
        f"Expected 0 findings on clean state, got {len(findings)}: {findings}"
    )
    print("  ✅ Clean state correctly produced 0 findings")
    return True


def test_redacted_values_ignored():
    """Attributes marked '(sensitive value)' should be skipped."""
    findings = scan_state_for_secrets(MOCK_STATE_REDACTED)
    assert len(findings) == 0, (
        f"Expected 0 findings on redacted state, got {len(findings)}: {findings}"
    )
    print("  ✅ Redacted '(sensitive value)' correctly ignored")
    return True


def test_empty_state():
    """Empty state should not crash."""
    findings = scan_state_for_secrets({})
    assert len(findings) == 0, (
        f"Expected 0 findings on empty state, got {len(findings)}"
    )
    print("  ✅ Empty state handled gracefully")
    return True


def test_no_secret_values_stored():
    """Verify that findings contain only paths/patterns, never actual secret values."""
    findings = scan_state_for_secrets(MOCK_STATE_WITH_SECRETS)
    for f in findings:
        keys = set(f.keys())
        assert keys == {"attribute_path", "pattern", "description"}, (
            f"Finding has unexpected keys: {keys}"
        )
        # No finding should contain the actual secret value
        assert "AKIA" not in f["description"], "Secret value leaked into description"
        assert "SuperSecret" not in f["description"], (
            "Secret value leaked into description"
        )
        assert "ghp_" not in f["description"], "Secret value leaked into description"
    print("  ✅ No secret values stored in findings (only paths and pattern names)")
    return True


# ----- Runner -----

if __name__ == "__main__":
    tests = [
        ("Detects known secrets", test_detects_secrets),
        ("Clean state = no findings", test_clean_state_no_findings),
        ("Redacted values ignored", test_redacted_values_ignored),
        ("Empty state handled", test_empty_state),
        ("No secret values stored", test_no_secret_values_stored),
    ]

    passed = 0
    failed = 0

    print("\n🔍 State Secrets Scan — Pattern Matching Tests\n")
    for name, test_fn in tests:
        print(f"Test: {name}")
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            print(f"  ❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")

    if failed > 0:
        sys.exit(1)
    else:
        print("✅ All tests passed!")
        sys.exit(0)
