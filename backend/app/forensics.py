"""
Merkle tree & forensic bundle creation + verify functions
"""
import hashlib
import json
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
import time


class MerkleTree:
    """Merkle tree implementation for forensic anchoring"""
    
    @staticmethod
    def hash_data(data: str) -> str:
        """Hash data using SHA-256"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def build_tree(hashes: List[str]) -> Dict:
        """Build Merkle tree from list of hashes"""
        if not hashes:
            return {"root": "", "tree": {}}
        
        # Ensure even number of leaves
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])
        
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
    def create_merkle_root(artifact_hashes: List[str]) -> str:
        """Create Merkle root from artifact hashes"""
        if not artifact_hashes:
            return ""
        
        tree = MerkleTree.build_tree(artifact_hashes)
        return tree["root"]
    
    @staticmethod
    def generate_proof(artifact_hashes: List[str], item_hash: str) -> List[str]:
        """Generate Merkle proof for an item"""
        # Simplified proof generation
        # In production, this would generate the actual path to root
        proof = []
        current_level = artifact_hashes.copy()
        
        if item_hash not in current_level:
            return []
        
        idx = current_level.index(item_hash)
        
        while len(current_level) > 1:
            sibling_idx = idx ^ 1  # XOR to get sibling
            if sibling_idx < len(current_level):
                proof.append(current_level[sibling_idx])
            
            # Move to parent level
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else current_level[i]
                combined = left + right
                parent_hash = MerkleTree.hash_data(combined)
                next_level.append(parent_hash)
            
            current_level = next_level
            idx = idx // 2
        
        return proof


def sign_stub(merkle_root: str) -> Dict:
    """
    Sign the Merkle root (stub - no real blockchain integration).
    Returns fake transaction ID for demonstration.
    """
    # In production, this would interact with a real blockchain
    # For now, generate a fake transaction hash
    fake_tx_data = f"{merkle_root}_{time.time()}"
    fake_tx_hash = hashlib.sha256(fake_tx_data.encode()).hexdigest()
    
    return {
        "tx_hash": fake_tx_hash,
        "blockchain": "stub",
        "timestamp": time.time(),
        "signed": True
    }


def verify_proof(root: str, proof: List[str], item_hash: str) -> bool:
    """Verify Merkle proof"""
    current_hash = item_hash
    
    for sibling_hash in proof:
        # Determine order (simplified - in production would track left/right)
        combined = current_hash + sibling_hash
        current_hash = MerkleTree.hash_data(combined)
    
    return current_hash == root


def create_forensic_bundle(alert_data: Dict, artifacts: List[Dict]) -> Dict:
    """
    Create forensic bundle with Merkle tree.
    
    Args:
        alert_data: Alert data dictionary
        artifacts: List of artifact dictionaries (each with 'hash' field)
    
    Returns:
        Forensic bundle dictionary
    """
    # Extract artifact hashes
    artifact_hashes = [art.get("hash") for art in artifacts if art.get("hash")]
    
    if not artifact_hashes:
        # If no artifacts, use alert data hash
        alert_str = json.dumps(alert_data, sort_keys=True)
        alert_hash = MerkleTree.hash_data(alert_str)
        artifact_hashes = [alert_hash]
    
    # Create Merkle root
    merkle_root = MerkleTree.create_merkle_root(artifact_hashes)
    
    # Generate proofs for each artifact
    proofs = {}
    for art in artifacts:
        if art.get("hash"):
            proof = MerkleTree.generate_proof(artifact_hashes, art["hash"])
            proofs[art["hash"]] = proof
    
    # Sign the root (stub)
    signature = sign_stub(merkle_root)
    
    # Create forensic bundle
    forensic_bundle = {
        "forensic_id": f"FORENSIC_{int(time.time() * 1000)}",
        "alert_id": alert_data.get("alert_id", "unknown"),
        "timestamp": time.time(),
        "datetime": datetime.now().isoformat(),
        "merkle_root": merkle_root,
        "artifacts": artifacts,
        "artifact_hashes": artifact_hashes,
        "proofs": proofs,
        "blockchain_tx_hash": signature.get("tx_hash"),
        "signature": signature
    }
    
    return forensic_bundle


def verify_forensic_bundle(forensic_bundle: Dict) -> bool:
    """Verify forensic bundle integrity"""
    merkle_root = forensic_bundle.get("merkle_root")
    artifacts = forensic_bundle.get("artifacts", [])
    proofs = forensic_bundle.get("proofs", {})
    
    if not merkle_root:
        return False
    
    # Verify each artifact's proof
    for art in artifacts:
        art_hash = art.get("hash")
        if art_hash and art_hash in proofs:
            proof = proofs[art_hash]
            if not verify_proof(merkle_root, proof, art_hash):
                return False
    
    return True

