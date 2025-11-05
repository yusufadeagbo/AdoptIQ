// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

contract CertificateRegistry is AccessControl, Pausable {
    bytes32 public constant ISSUER_ROLE = keccak256("ISSUER_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");

    enum CertificateType {
        AUDIT,
        MISSION_COMPLETION,
        VERIFICATION
    }

    struct Certificate {
        bytes32 certificateId;
        CertificateType certType;
        address issuer;
        address subject;
        string ipfsHash;
        bytes32 contentHash;
        uint256 issuedAt;
        uint256 expiresAt;
        bool revoked;
        string metadata;
    }

    mapping(bytes32 => Certificate) public certificates;
    mapping(address => bytes32[]) public subjectCertificates;
    mapping(bytes32 => bool) public exists;

    uint256 public totalCertificatesIssued;
    uint256 public totalRevoked;

    event CertificateIssued(
        bytes32 indexed certificateId,
        CertificateType certType,
        address indexed issuer,
        address indexed subject,
        string ipfsHash,
        bytes32 contentHash,
        uint256 timestamp
    );

    event CertificateRevoked(
        bytes32 indexed certificateId,
        address indexed revoker,
        uint256 timestamp
    );

    event CertificateVerified(
        bytes32 indexed certificateId,
        address indexed verifier,
        uint256 timestamp
    );

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(ISSUER_ROLE, msg.sender);
    }

    function issueCertificate(
        bytes32 certificateId,
        CertificateType certType,
        address subject,
        string memory ipfsHash,
        bytes32 contentHash,
        uint256 expiresAt,
        string memory metadata
    ) external whenNotPaused onlyRole(ISSUER_ROLE) {
        require(!exists[certificateId], "Certificate already exists");
        require(subject != address(0), "Invalid subject address");
        require(bytes(ipfsHash).length > 0, "IPFS hash required");
        require(contentHash != bytes32(0), "Content hash required");

        Certificate memory cert = Certificate({
            certificateId: certificateId,
            certType: certType,
            issuer: msg.sender,
            subject: subject,
            ipfsHash: ipfsHash,
            contentHash: contentHash,
            issuedAt: block.timestamp,
            expiresAt: expiresAt,
            revoked: false,
            metadata: metadata
        });

        certificates[certificateId] = cert;
        subjectCertificates[subject].push(certificateId);
        exists[certificateId] = true;
        totalCertificatesIssued++;

        emit CertificateIssued(
            certificateId,
            certType,
            msg.sender,
            subject,
            ipfsHash,
            contentHash,
            block.timestamp
        );
    }

    function revokeCertificate(bytes32 certificateId) external onlyRole(ISSUER_ROLE) {
        require(exists[certificateId], "Certificate does not exist");
        Certificate storage cert = certificates[certificateId];
        require(!cert.revoked, "Already revoked");
        require(cert.issuer == msg.sender || hasRole(ADMIN_ROLE, msg.sender), "Not authorized");

        cert.revoked = true;
        totalRevoked++;

        emit CertificateRevoked(certificateId, msg.sender, block.timestamp);
    }

    function verifyCertificate(bytes32 certificateId) external view returns (bool) {
        if (!exists[certificateId]) {
            return false;
        }

        Certificate memory cert = certificates[certificateId];

        if (cert.revoked) {
            return false;
        }

        if (cert.expiresAt > 0 && block.timestamp > cert.expiresAt) {
            return false;
        }

        return true;
    }

    function getCertificate(bytes32 certificateId) external view returns (
        CertificateType certType,
        address issuer,
        address subject,
        string memory ipfsHash,
        bytes32 contentHash,
        uint256 issuedAt,
        uint256 expiresAt,
        bool revoked,
        string memory metadata
    ) {
        require(exists[certificateId], "Certificate does not exist");
        Certificate memory cert = certificates[certificateId];

        return (
            cert.certType,
            cert.issuer,
            cert.subject,
            cert.ipfsHash,
            cert.contentHash,
            cert.issuedAt,
            cert.expiresAt,
            cert.revoked,
            cert.metadata
        );
    }

    function getSubjectCertificates(address subject) external view returns (bytes32[] memory) {
        return subjectCertificates[subject];
    }

    function verifyContentHash(bytes32 certificateId, bytes32 contentHash) external view returns (bool) {
        require(exists[certificateId], "Certificate does not exist");
        Certificate memory cert = certificates[certificateId];

        return cert.contentHash == contentHash && !cert.revoked;
    }

    function pause() external onlyRole(ADMIN_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }
}
