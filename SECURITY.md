# Security Documentation - SentinelVNC v2

## Overview

SentinelVNC v2 implements government-grade security measures for protecting sensitive VNC session monitoring and intrusion detection data.

## Authentication & Authorization

### JWT-Based Authentication
- **Access Tokens**: Short-lived (30 minutes default)
- **Refresh Tokens**: Long-lived (7 days default), stored in database
- **Algorithm**: HS256 (configurable)
- **Secret Key**: Must be strong, randomly generated (minimum 32 characters)

### Role-Based Access Control (RBAC)
- **Admin**: Full system access, user management
- **Analyst**: Alert management, detection configuration
- **Read-Only**: View-only access to alerts and dashboards

### Two-Factor Authentication (2FA)
- **Method**: TOTP (Time-based One-Time Password)
- **Implementation**: Google Authenticator compatible
- **QR Code**: Generated during setup
- **Validity Window**: 1 time step (30 seconds)

### Password Security
- **Hashing**: bcrypt with automatic salt
- **Minimum Length**: Enforced at application level
- **Failed Login Protection**: Account lockout after 5 failed attempts
- **Lockout Duration**: 15 minutes (configurable)

## Data Encryption

### Data in Transit
- **HTTPS/TLS**: Required for all API communications
- **Certificate**: Self-signed or CA-signed (configurable)
- **TLS Version**: 1.2 minimum

### Data at Rest
- **Encryption**: AES-256
- **Key Management**: Environment variables or key management service
- **Key Rotation**: Every 30 days (configurable)

### Database Encryption
- **PostgreSQL**: Encrypted connections (SSL)
- **MongoDB**: Encrypted connections (TLS)
- **Sensitive Fields**: Hashed or encrypted before storage

## Network Security

### Firewall Rules
- **API Port**: 8000 (internal only, use reverse proxy)
- **Dashboard Port**: 8501 (HTTPS only)
- **Database Ports**: Not exposed externally
- **Redis Port**: Not exposed externally

### Rate Limiting
- **API Endpoints**: 60 requests per minute per user
- **Login Endpoints**: 5 attempts per 15 minutes
- **Detection Endpoints**: 100 requests per minute

## Security Headers

### HTTP Security Headers
- **X-Content-Type-Options**: nosniff
- **X-Frame-Options**: DENY
- **X-XSS-Protection**: 1; mode=block
- **Strict-Transport-Security**: max-age=31536000
- **Content-Security-Policy**: Strict policy

## Audit Logging

### Audit Events
- User authentication (login, logout, failed attempts)
- User management (create, update, delete)
- Alert management (create, update, contain)
- Configuration changes
- System access

### Log Storage
- **PostgreSQL**: Structured audit logs
- **MongoDB**: Raw event logs
- **Retention**: 90 days (configurable)
- **Archival**: Automatic after retention period

## Key Management

### Secret Keys
- **JWT Secret**: Separate from application secret
- **Encryption Key**: 32+ character random string
- **Database Passwords**: Strong, unique per environment
- **Rotation**: Every 30 days (configurable)

### Environment Variables
- All secrets stored in environment variables
- `.env` file excluded from version control
- `.env.example` provided as template

## Container Security

### Docker Security
- **Non-root User**: Containers run as non-root
- **Read-only Filesystems**: Where possible
- **Minimal Base Images**: Alpine Linux
- **Security Scanning**: Regular vulnerability scans

### SELinux/AppArmor
- **Profiles**: Applied to containers
- **Sandboxing**: AI inference processes isolated

## API Security

### Input Validation
- **Pydantic Models**: All inputs validated
- **SQL Injection**: Prevented via SQLAlchemy ORM
- **XSS Protection**: Input sanitization
- **CSRF Protection**: Token-based

### Authentication
- **Bearer Tokens**: JWT in Authorization header
- **Token Validation**: On every request
- **Token Revocation**: Supported via refresh token revocation

## Blockchain & Forensics

### Merkle Tree Anchoring
- **Algorithm**: SHA-256
- **Integrity**: Tamper-proof evidence
- **Verification**: Automatic on retrieval

### Forensic Evidence
- **Hash Verification**: SHA-256 hashes
- **Timestamp**: UTC timestamps
- **Chain of Custody**: Logged in audit trail

## Compliance

### OWASP Top 10
- **A01:2021 – Broken Access Control**: RBAC implemented
- **A02:2021 – Cryptographic Failures**: Strong encryption
- **A03:2021 – Injection**: ORM prevents SQL injection
- **A04:2021 – Insecure Design**: Security by design
- **A05:2021 – Security Misconfiguration**: Secure defaults
- **A06:2021 – Vulnerable Components**: Regular updates
- **A07:2021 – Authentication Failures**: Strong auth
- **A08:2021 – Software and Data Integrity**: Blockchain anchoring
- **A09:2021 – Security Logging Failures**: Comprehensive logging
- **A10:2021 – Server-Side Request Forgery**: Input validation

## Security Best Practices

### Development
1. Never commit secrets to version control
2. Use strong, unique passwords
3. Enable 2FA for all admin accounts
4. Regular security audits
5. Dependency vulnerability scanning

### Deployment
1. Use HTTPS in production
2. Rotate keys regularly
3. Monitor audit logs
4. Regular backups
5. Disaster recovery plan

### Operations
1. Regular security updates
2. Monitor failed login attempts
3. Review audit logs weekly
4. Incident response plan
5. Security training for operators

## Incident Response

### Security Incident Procedure
1. **Detection**: Automated alerts for suspicious activity
2. **Containment**: Immediate account lockout if compromised
3. **Investigation**: Audit log analysis
4. **Recovery**: Password reset, key rotation
5. **Documentation**: Incident report

### Contact
- **Security Team**: security@sentinelvnc.local
- **Emergency**: Follow organization's incident response plan

## Updates

This security documentation is updated regularly. Last updated: 2024-01-XX

