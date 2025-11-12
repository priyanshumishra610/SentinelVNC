"""
Unit tests for merkle_anchor.py
"""
import pytest
import json
import time
from pathlib import Path
from merkle_anchor import MerkleTree, ForensicAnchoring


class TestMerkleTree:
    """Test MerkleTree class."""
    
    def test_hash_data(self):
        """Test hash_data function."""
        data = "test data"
        hash1 = MerkleTree.hash_data(data)
        hash2 = MerkleTree.hash_data(data)
        
        assert hash1 == hash2  # Same input produces same hash
        assert len(hash1) == 64  # SHA-256 hex digest length
        assert hash1 != MerkleTree.hash_data("different data")
    
    def test_build_tree_empty(self):
        """Test build_tree with empty list."""
        tree = MerkleTree.build_tree([])
        
        assert tree["root"] == ""
        assert "tree" in tree
    
    def test_build_tree_single_hash(self):
        """Test build_tree with single hash."""
        hashes = ["abc123"]
        tree = MerkleTree.build_tree(hashes)
        
        assert tree["root"] != ""
        assert "leaves" in tree["tree"]
    
    def test_build_tree_multiple_hashes(self):
        """Test build_tree with multiple hashes."""
        hashes = [MerkleTree.hash_data(f"data{i}") for i in range(4)]
        tree = MerkleTree.build_tree(hashes)
        
        assert tree["root"] != ""
        assert len(tree["tree"]["leaves"]) == 4
    
    def test_build_tree_odd_number(self):
        """Test build_tree with odd number of hashes."""
        hashes = [MerkleTree.hash_data(f"data{i}") for i in range(3)]
        tree = MerkleTree.build_tree(hashes)
        
        assert tree["root"] != ""
        # Should duplicate last hash to make even
        assert len(tree["tree"]["leaves"]) >= 3
    
    def test_create_merkle_root_no_files(self, temp_dir):
        """Test create_merkle_root with no files."""
        forensic_files = []
        root = MerkleTree.create_merkle_root(forensic_files)
        
        assert root == ""
    
    def test_create_merkle_root_with_files(self, temp_dir, forensic_dir):
        """Test create_merkle_root with forensic files."""
        # Create test forensic files
        for i in range(3):
            forensic_file = forensic_dir / f"forensic_{i}.json"
            data = {
                "forensic_id": f"FORENSIC_{i}",
                "timestamp": time.time() + i,
                "event_type": "clipboard_copy"
            }
            with open(forensic_file, 'w') as f:
                json.dump(data, f)
        
        forensic_files = list(forensic_dir.glob("*.json"))
        root = MerkleTree.create_merkle_root(forensic_files)
        
        assert root != ""
        assert len(root) == 64  # SHA-256 hex digest
    
    def test_create_merkle_root_deterministic(self, temp_dir, forensic_dir):
        """Test that Merkle root is deterministic."""
        # Create test forensic files
        for i in range(2):
            forensic_file = forensic_dir / f"forensic_{i}.json"
            data = {
                "forensic_id": f"FORENSIC_{i}",
                "timestamp": time.time() + i,
                "event_type": "clipboard_copy"
            }
            with open(forensic_file, 'w') as f:
                json.dump(data, f)
        
        forensic_files = list(forensic_dir.glob("*.json"))
        root1 = MerkleTree.create_merkle_root(forensic_files)
        root2 = MerkleTree.create_merkle_root(forensic_files)
        
        assert root1 == root2  # Same files produce same root


class TestForensicAnchoring:
    """Test ForensicAnchoring class."""
    
    def test_init(self, temp_dir):
        """Test ForensicAnchoring initialization."""
        anchorer = ForensicAnchoring(
            forensic_dir=str(temp_dir / "forensic"),
            anchors_dir=str(temp_dir / "anchors")
        )
        
        assert anchorer.forensic_dir.exists()
        assert anchorer.anchors_dir.exists()
    
    def test_create_anchor_no_forensic_files(self, temp_dir):
        """Test create_anchor with no forensic files."""
        anchorer = ForensicAnchoring(
            forensic_dir=str(temp_dir / "forensic"),
            anchors_dir=str(temp_dir / "anchors")
        )
        
        anchor = anchorer.create_anchor()
        
        assert anchor == {}
    
    def test_create_anchor_with_files(self, temp_dir, forensic_dir, anchors_dir):
        """Test create_anchor with forensic files."""
        anchorer = ForensicAnchoring(
            forensic_dir=str(forensic_dir),
            anchors_dir=str(anchors_dir)
        )
        
        # Create test forensic files
        for i in range(3):
            forensic_file = forensic_dir / f"forensic_{i}.json"
            data = {
                "forensic_id": f"FORENSIC_{i}",
                "timestamp": time.time() + i,
                "event_type": "clipboard_copy",
                "hash": f"hash_{i}"
            }
            with open(forensic_file, 'w') as f:
                json.dump(data, f)
        
        anchor = anchorer.create_anchor()
        
        assert anchor != {}
        assert "anchor_id" in anchor
        assert "merkle_root" in anchor
        assert "forensic_count" in anchor
        assert anchor["forensic_count"] == 3
        assert "signature_hash" in anchor
        
        # Check anchor file was created
        anchor_file = anchors_dir / f"{anchor['anchor_id']}.json"
        assert anchor_file.exists()
    
    def test_create_anchor_custom_id(self, temp_dir, forensic_dir, anchors_dir):
        """Test create_anchor with custom anchor ID."""
        anchorer = ForensicAnchoring(
            forensic_dir=str(forensic_dir),
            anchors_dir=str(anchors_dir)
        )
        
        # Create test forensic file
        forensic_file = forensic_dir / "forensic_0.json"
        data = {"forensic_id": "FORENSIC_0", "timestamp": time.time()}
        with open(forensic_file, 'w') as f:
            json.dump(data, f)
        
        anchor = anchorer.create_anchor(anchor_id="CUSTOM_ANCHOR_123")
        
        assert anchor["anchor_id"] == "CUSTOM_ANCHOR_123"
        anchor_file = anchors_dir / "CUSTOM_ANCHOR_123.json"
        assert anchor_file.exists()
    
    def test_verify_anchor_valid(self, temp_dir, forensic_dir, anchors_dir):
        """Test verify_anchor with valid anchor."""
        anchorer = ForensicAnchoring(
            forensic_dir=str(forensic_dir),
            anchors_dir=str(anchors_dir)
        )
        
        # Create test forensic files
        for i in range(2):
            forensic_file = forensic_dir / f"forensic_{i}.json"
            data = {
                "forensic_id": f"FORENSIC_{i}",
                "timestamp": time.time() + i
            }
            with open(forensic_file, 'w') as f:
                json.dump(data, f)
        
        anchor = anchorer.create_anchor()
        anchor_file = anchors_dir / f"{anchor['anchor_id']}.json"
        
        result = anchorer.verify_anchor(anchor_file)
        
        assert result is True
    
    def test_verify_anchor_invalid(self, temp_dir, forensic_dir, anchors_dir):
        """Test verify_anchor with tampered forensic files."""
        anchorer = ForensicAnchoring(
            forensic_dir=str(forensic_dir),
            anchors_dir=str(anchors_dir)
        )
        
        # Create test forensic files
        for i in range(2):
            forensic_file = forensic_dir / f"forensic_{i}.json"
            data = {
                "forensic_id": f"FORENSIC_{i}",
                "timestamp": time.time() + i
            }
            with open(forensic_file, 'w') as f:
                json.dump(data, f)
        
        anchor = anchorer.create_anchor()
        anchor_file = anchors_dir / f"{anchor['anchor_id']}.json"
        
        # Tamper with forensic file
        forensic_file = forensic_dir / "forensic_0.json"
        with open(forensic_file, 'w') as f:
            json.dump({"forensic_id": "TAMPERED", "timestamp": time.time()}, f)
        
        result = anchorer.verify_anchor(anchor_file)
        
        assert result is False
    
    def test_verify_anchor_nonexistent(self, temp_dir, anchors_dir):
        """Test verify_anchor with nonexistent file."""
        anchorer = ForensicAnchoring(
            forensic_dir=str(temp_dir / "forensic"),
            anchors_dir=str(anchors_dir)
        )
        
        nonexistent_file = anchors_dir / "nonexistent.json"
        result = anchorer.verify_anchor(nonexistent_file)
        
        assert result is False
    
    def test_list_anchors(self, temp_dir, forensic_dir, anchors_dir):
        """Test list_anchors function."""
        anchorer = ForensicAnchoring(
            forensic_dir=str(forensic_dir),
            anchors_dir=str(anchors_dir)
        )
        
        # Create test forensic files
        for i in range(2):
            forensic_file = forensic_dir / f"forensic_{i}.json"
            data = {"forensic_id": f"FORENSIC_{i}", "timestamp": time.time() + i}
            with open(forensic_file, 'w') as f:
                json.dump(data, f)
        
        # Create multiple anchors
        anchor1 = anchorer.create_anchor(anchor_id="ANCHOR_1")
        time.sleep(0.1)
        anchor2 = anchorer.create_anchor(anchor_id="ANCHOR_2")
        
        anchors = anchorer.list_anchors()
        
        assert len(anchors) == 2
        assert anchors[0]["anchor_id"] == "ANCHOR_1"  # Sorted by timestamp
        assert anchors[1]["anchor_id"] == "ANCHOR_2"



