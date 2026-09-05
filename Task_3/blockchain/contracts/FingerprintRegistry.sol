// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @notice Reference contract only. Do not store raw images or biometrics on-chain.
contract FingerprintRegistry {
    struct Proof { string sourceUrl; uint256 recordedAt; address recorder; }
    mapping(bytes32 => Proof) public proofs;
    event ProofRecorded(bytes32 indexed fingerprint, string sourceUrl, address indexed recorder);

    function record(bytes32 fingerprint, string calldata sourceUrl) external {
        require(proofs[fingerprint].recordedAt == 0, "already recorded");
        proofs[fingerprint] = Proof(sourceUrl, block.timestamp, msg.sender);
        emit ProofRecorded(fingerprint, sourceUrl, msg.sender);
    }
}

