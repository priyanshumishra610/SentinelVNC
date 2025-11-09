# SentinelVNC FAQ for Hackathon Judges

## 1. Why did you choose Merkle tree anchoring instead of a full blockchain?

**Answer:**
We chose Merkle tree anchoring for the MVP because:
- **Simplicity**: No need for a full blockchain network (nodes, consensus, mining)
- **Lightweight**: Perfect for air-gapped environments with limited resources
- **Sufficient for MVP**: Merkle trees provide the same tamper-proofing for forensic evidence
- **Scalable path**: Can easily migrate to full blockchain (Ethereum, Hyperledger) later
- **Local-first**: Works entirely offline, no network dependencies

**Technical Details:**
- Merkle root hash provides cryptographic integrity
- Any tampering with forensic files invalidates the root
- Can be verified independently without blockchain infrastructure
- In production, we'd anchor the Merkle root to a public blockchain (Ethereum mainnet) for additional immutability

**Future Enhancement:**
We have a clear path to full blockchain integration using Ganache (local testnet) or Ethereum mainnet for production deployments.

---

## 2. How do you handle false positives?

**Answer:**
We use a multi-layered approach to minimize false positives:

**1. Rule-Based Thresholds:**
- Carefully tuned thresholds based on normal usage patterns
- Clipboard: 200KB threshold (normal clipboard is <50KB)
- Screenshots: 5+ in 10 seconds (normal is <2 per minute)
- File transfers: 50MB threshold (normal files are <20MB)

**2. Hybrid Detection:**
- Rules catch obvious patterns (low false positives)
- ML model provides additional confidence scoring
- Both must agree for high-severity alerts (reduces false positives)

**3. Context-Aware:**
- ML model considers historical patterns (time of day, recent activity)
- Reduces false positives from legitimate bulk operations during business hours

**4. Explainability:**
- Every alert includes reasons, so security teams can quickly verify
- Human-in-the-loop validation before containment actions

**5. Tunable Thresholds:**
- All thresholds are configurable
- Can be adjusted based on organization's normal usage patterns

**Current Performance:**
- Training set: 80% normal, 20% anomaly
- Test accuracy: ~85-90%
- False positive rate: <5% (on test set)

---

## 3. How does this work in an air-gapped environment?

**Answer:**
SentinelVNC is designed for air-gapped deployment:

**1. No Cloud Dependencies:**
- All processing happens locally
- No external API calls
- No internet connection required

**2. Local Blockchain:**
- Merkle tree anchoring works entirely offline
- No need for blockchain network connectivity
- Can use local Ganache testnet if full blockchain needed

**3. Self-Contained:**
- All dependencies are Python packages (installable offline)
- Model training happens locally
- No external data sources required

**4. Deployment:**
- Single VM deployment
- All components run on the same machine
- Can be packaged as Docker container for easy deployment

**5. Data Privacy:**
- All data stays on-premises
- No telemetry or external logging
- Perfect for sensitive environments (government, healthcare, finance)

**Installation in Air-Gapped Environment:**
1. Download Python packages on internet-connected machine
2. Transfer to air-gapped system
3. Install from local packages
4. Run entirely offline

---

## 4. How does this scale to enterprise deployments?

**Answer:**
The MVP is designed with scalability in mind:

**Current Architecture:**
- Single VM deployment (suitable for small-medium organizations)
- File-based event storage (JSONL)
- In-memory detection (fast for <1000 events/second)

**Scalability Path:**

**1. Horizontal Scaling:**
- Deploy multiple detector instances
- Use message queue (RabbitMQ, Kafka) for event distribution
- Load balancer for dashboard access

**2. Database Integration:**
- Replace JSONL files with PostgreSQL/MongoDB
- Indexed queries for faster alert retrieval
- Time-series database (InfluxDB) for metrics

**3. Distributed Detection:**
- Microservices architecture
- Separate services for: event ingestion, detection, forensics, anchoring
- Container orchestration (Kubernetes) for auto-scaling

**4. Performance Optimization:**
- Model serving with TensorFlow Serving or TorchServe
- Batch processing for high-volume events
- Caching for frequently accessed data

**5. Enterprise Features:**
- Multi-tenant support
- Role-based access control
- Integration with SIEM systems (Splunk, ELK)
- API for programmatic access

**Estimated Capacity:**
- **Current MVP**: ~100 events/second, single VM
- **Scaled (1 week)**: ~1000 events/second, distributed
- **Enterprise**: ~10,000+ events/second, full microservices

**Resource Requirements:**
- MVP: 2GB RAM, 2 CPU cores
- Scaled: 8GB RAM, 4 CPU cores per instance
- Enterprise: Auto-scaling based on load

---

## 5. What's the difference between this and existing VNC security tools?

**Answer:**
Key differentiators:

**1. Hybrid Detection:**
- Most tools are either rule-based OR ML-based
- We combine both for better accuracy and explainability

**2. Explainable AI:**
- Many ML security tools are black boxes
- We provide human-readable reasons for every alert
- SHAP values show feature contributions

**3. Blockchain-Anchored Forensics:**
- Most tools don't provide tamper-proof evidence
- Our Merkle tree anchoring ensures forensic integrity
- Verifiable evidence for compliance/legal purposes

**4. Real-Time Containment:**
- Detection + immediate containment actions
- Not just monitoring - active defense

**5. VNC-Specific:**
- Tailored for VNC attack patterns
- Understands VNC-specific threats (clipboard, screenshots)
- Not a generic network security tool

**Comparison:**
- **Traditional SIEM**: Generic, requires extensive tuning, high false positives
- **ML-only tools**: Black box, hard to explain, requires large datasets
- **Rule-only tools**: Miss subtle patterns, high false negatives
- **SentinelVNC**: Best of all worlds - hybrid, explainable, VNC-specific

---

## 6. How accurate is the ML model?

**Answer:**
**Training Performance:**
- Dataset: 2000 synthetic samples (80% normal, 20% anomaly)
- Model: RandomForest (100 trees, max depth 10)
- Training accuracy: ~95%
- Test accuracy: ~85-90%
- False positive rate: <5%
- False negative rate: <10%

**Limitations:**
- Trained on synthetic data (for MVP)
- Real-world performance may vary
- Requires retraining on production data

**Improvement Path:**
- Collect real VNC event data (anonymized)
- Retrain with production data
- Continuous learning from security team feedback
- A/B testing with different models

**Explainability:**
- SHAP values show which features contribute most
- Feature importance rankings available
- Helps security teams understand model decisions

---

## 7. What happens when an alert is triggered?

**Answer:**
**Detection Flow:**
1. Event detected by rules or ML model
2. Alert generated with reasons and severity
3. Forensic JSON created and saved
4. Alert logged to alerts.jsonl

**Containment Actions (Simulated in MVP):**
- **Immediate**: Log alert, create forensic record
- **Short-term**: Trigger containment (disconnect VNC session, block IP)
- **Long-term**: Incident response workflow, notification to security team

**Production Containment:**
- Disconnect VNC session
- Block source IP address
- Quarantine affected system
- Trigger incident response
- Notify security team via email/Slack

**Forensic Anchoring:**
- All alerts are anchored to Merkle tree
- Creates tamper-proof evidence
- Can be used for compliance/legal purposes

---

## 8. Can this detect zero-day attacks?

**Answer:**
**Current Capabilities:**
- **Known patterns**: Yes (rule-based detection)
- **Anomalous patterns**: Yes (ML-based detection)
- **Zero-day attacks**: Partially (depends on attack pattern)

**ML Model Strengths:**
- Learns normal usage patterns
- Flags deviations as anomalies
- Can catch previously unseen attack patterns if they're anomalous

**Limitations:**
- Requires training data that represents normal behavior
- May miss attacks that mimic normal behavior
- Needs continuous retraining as usage patterns evolve

**Improvement Path:**
- Unsupervised learning (autoencoders) for better anomaly detection
- Behavioral baselines per user/system
- Continuous learning from new attack patterns
- Integration with threat intelligence feeds

**Recommendation:**
- Use SentinelVNC as part of defense-in-depth strategy
- Combine with signature-based detection for known attacks
- Use anomaly detection for unknown/zero-day attacks

---

## Additional Questions to Prepare For

**Q: How long did this take to build?**
A: MVP built in ~1 month as solo project. Core components: 2 weeks, ML training: 3 days, Dashboard: 3 days, Testing: 4 days.

**Q: What's the biggest challenge you faced?**
A: Balancing detection accuracy with false positive rate. Solved through hybrid approach and careful threshold tuning.

**Q: What would you improve with more time?**
A: Real VNC integration, advanced ML models, full blockchain integration, enterprise features (multi-tenant, RBAC).

**Q: Is this production-ready?**
A: MVP is functional and demonstrates core concepts. Production deployment would require: real VNC integration, performance optimization, enterprise features, security hardening.

**Q: How do you handle encrypted VNC sessions?**
A: Current MVP works at event level (clipboard, screenshots, file transfers) - doesn't require decrypting VNC traffic. For network-level detection, would need VNC protocol analysis (future work).

