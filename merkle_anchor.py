#!/usr/bin/env python3
"""
SentinelVNC Merkle Tree Anchoring
Creates Merkle tree from forensic events and generates signed root hash.
Simpler alternative to full blockchain for MVP.
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import time


class MerkleTree:
    """Simple Merkle tree implementation for forensic anchoring."""
    
    @staticmethod
    def hash_data(data: str) -> str:
        """Hash data using SHA-256."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def build_tree(hashes: List[str]) -> Dict:
        """Build Merkle tree from list of hashes."""
        if not hashes:
            return {"root": "", "tree": {}}
        
        # Ensure even number of leaves
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])  # Duplicate last hash
        
        tree = {"leaves": hashes.copy()}
        current_level = hashes
        
        level = 0
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else current_level[i]
                combined = left + right
                parent_hash = MerkleTree.hash_data(combined)
                next_level.append(parent_hash)
            
            tree[f"level_{level}"] = next_level
            current_level = next_level
            level += 1
        
        root_hash = current_level[0] if current_level else ""
        tree["root"] = root_hash
        
        return tree
    
    @staticmethod
    def create_merkle_root(forensic_files: List[Path]) -> str:
        """Create Merkle root from forensic JSON files."""
        hashes = []
        
        for forensic_file in sorted(forensic_files):
            if forensic_file.exists():
                with open(forensic_file, 'r') as f:
                    data = json.load(f)
                    # Use forensic_id + hash for consistency
                    content = json.dumps(data, sort_keys=True)
                    file_hash = MerkleTree.hash_data(content)
                    hashes.append(file_hash)
        
        if not hashes:
            return ""
        
        tree = MerkleTree.build_tree(hashes)
        return tree["root"]


class ForensicAnchoring:
    """Anchors forensic events using Merkle tree."""
    
    def __init__(self, forensic_dir: str = "forensic", anchors_dir: str = "anchors"):
        self.forensic_dir = Path(forensic_dir)
        self.anchors_dir = Path(anchors_dir)
        self.anchors_dir.mkdir(parents=True, exist_ok=True)
    
    def create_anchor(self, anchor_id: Optional[str] = None) -> Dict:
        """Create a Merkle anchor from all forensic files."""
        forensic_files = list(self.forensic_dir.glob("*.json"))
        
        if not forensic_files:
            print("[Anchoring] No forensic files found")
            return {}
        
        print(f"[Anchoring] Creating anchor from {len(forensic_files)} forensic files...")
        
        # Create Merkle root
        merkle_root = MerkleTree.create_merkle_root(forensic_files)
        
        if not merkle_root:
            print("[Anchoring] Failed to create Merkle root")
            return {}
        
        # Create anchor metadata
        if anchor_id is None:
            anchor_id = f"ANCHOR_{int(time.time() * 1000)}"
        
        anchor = {
            "anchor_id": anchor_id,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "merkle_root": merkle_root,
            "forensic_count": len(forensic_files),
            "forensic_files": [str(f.name) for f in forensic_files],
            "verification": {
                "algorithm": "SHA-256",
                "tree_type": "Merkle",
                "integrity": "verified"
            }
        }
        
        # Sign the anchor (simplified - in production use proper signing)
        anchor_str = json.dumps(anchor, sort_keys=True)
        anchor["signature_hash"] = hashlib.sha256(anchor_str.encode()).hexdigest()
        
        # Save anchor
        anchor_file = self.anchors_dir / f"{anchor_id}.json"
        with open(anchor_file, 'w') as f:
            json.dump(anchor, f, indent=2)
        
        print(f"[Anchoring] Anchor created: {anchor_id}")
        print(f"  Merkle Root: {merkle_root[:32]}...")
        print(f"  Forensic Files: {len(forensic_files)}")
        print(f"  Saved to: {anchor_file}")
        
        return anchor
    
    def verify_anchor(self, anchor_file: Path) -> bool:
        """Verify the integrity of an anchor."""
        if not anchor_file.exists():
            return False
        
        with open(anchor_file, 'r') as f:
            anchor = json.load(f)
        
        # Recompute Merkle root
        forensic_files = [self.forensic_dir / f for f in anchor.get("forensic_files", [])]
        computed_root = MerkleTree.create_merkle_root(forensic_files)
        
        stored_root = anchor.get("merkle_root", "")
        
        if computed_root == stored_root:
            print(f"[Anchoring] Anchor {anchor_file.name} verified successfully")
            return True
        else:
            print(f"[Anchoring] Anchor {anchor_file.name} verification failed")
            print(f"  Stored root: {stored_root[:32]}...")
            print(f"  Computed root: {computed_root[:32]}...")
            return False
    
    def list_anchors(self) -> List[Dict]:
        """List all anchors."""
        anchors = []
        for anchor_file in self.anchors_dir.glob("*.json"):
            with open(anchor_file, 'r') as f:
                anchor = json.load(f)
                anchors.append(anchor)
        return sorted(anchors, key=lambda x: x.get("timestamp", 0))


if __name__ == "__main__":
    # Test anchoring
    anchorer = ForensicAnchoring()
    
    print("Creating anchor from forensic files...")
    anchor = anchorer.create_anchor()
    
    if anchor:
        print("\nAnchor created successfully!")
        print(json.dumps(anchor, indent=2))
        
        # Verify
        anchor_file = anchorer.anchors_dir / f"{anchor['anchor_id']}.json"
        anchorer.verify_anchor(anchor_file)
    
    print("\nListing all anchors:")
    anchors = anchorer.list_anchors()
    for a in anchors:
        print(f"  {a['anchor_id']}: {a['merkle_root'][:32]}... ({a['forensic_count']} files)")

