"""
Tests for forensics module
"""
import pytest
from backend.app.forensics import (
    MerkleTree, create_forensic_bundle, verify_forensic_bundle,
    verify_proof, sign_stub
)


def test_merkle_tree():
    """Test Merkle tree creation"""
    hashes = ["hash1", "hash2", "hash3", "hash4"]
    root = MerkleTree.create_merkle_root(hashes)
    
    assert root is not None
    assert len(root) == 64  # SHA-256 hex string


def test_merkle_tree_single():
    """Test Merkle tree with single hash"""
    hashes = ["hash1"]
    root = MerkleTree.create_merkle_root(hashes)
    
    assert root is not None


def test_merkle_tree_empty():
    """Test Merkle tree with empty list"""
    hashes = []
    root = MerkleTree.create_merkle_root(hashes)
    
    assert root == ""


def test_sign_stub():
    """Test signature stub"""
    merkle_root = "test_root_hash"
    signature = sign_stub(merkle_root)
    
    assert "tx_hash" in signature
    assert "blockchain" in signature
    assert signature["signed"] is True


def test_create_forensic_bundle():
    """Test forensic bundle creation"""
    alert_data = {
        "alert_id": "ALERT_123",
        "timestamp": 1000.0
    }
    
    artifacts = [
        {"hash": "artifact1", "type": "sample"},
        {"hash": "artifact2", "type": "sample"}
    ]
    
    bundle = create_forensic_bundle(alert_data, artifacts)
    
    assert "forensic_id" in bundle
    assert "merkle_root" in bundle
    assert "artifacts" in bundle
    assert "blockchain_tx_hash" in bundle
    assert bundle["alert_id"] == "ALERT_123"


def test_verify_forensic_bundle():
    """Test forensic bundle verification"""
    alert_data = {
        "alert_id": "ALERT_123",
        "timestamp": 1000.0
    }
    
    artifacts = [
        {"hash": "artifact1", "type": "sample"},
        {"hash": "artifact2", "type": "sample"}
    ]
    
    bundle = create_forensic_bundle(alert_data, artifacts)
    
    # Verification should pass for valid bundle
    verified = verify_forensic_bundle(bundle)
    assert verified is True


def test_verify_proof():
    """Test Merkle proof verification"""
    hashes = ["hash1", "hash2", "hash3", "hash4"]
    root = MerkleTree.create_merkle_root(hashes)
    
    # Generate proof for first hash
    proof = MerkleTree.generate_proof(hashes, "hash1")
    
    # Verify proof
    verified = verify_proof(root, proof, "hash1")
    assert verified is True

