// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract NusaCareAuditAndAccess {
    // Struktur data untuk mencatat riwayat data medis/rekomendasi
    struct DataRecord {
        address userAddress;      // Alamat pengguna (Pasien/Dokter)
        string cid;               // Content Identifier (Hash IPFS)
        string dataType;          // MEDICAL_RECORD, HERBAL_DATA, or RECOMMENDATION_RESULT
        uint256 timestamp;        // Waktu pencatatan
    }

    // Peta untuk menyimpan izin akses Pasien ke Dokter
    // Mapping: PatientAddress => DoctorAddress => HasPermission
    mapping(address => mapping(address => bool)) public accessPermissions;

    // Array untuk mencatat semua transaksi data (Audit Trail)
    DataRecord[] public dataRecords;

    // Fungsi untuk Mencatat CID ke Blockchain (Audit Trail) [cite: 540]
    function recordData(address _userAddress, string memory _cid, string memory _dataType) public {
        // Hanya alamat yang disetujui (misal: backend service wallet) yang dapat memanggil fungsi ini
        dataRecords.push(DataRecord(
            _userAddress,
            _cid,
            _dataType,
            block.timestamp
        ));
        // Catatan: Hash transaksi akan menjadi rekam jejak permanen [cite: 511]
    }

    // Fungsi untuk Memberi/Mencabut Izin Akses (Smart Contract Kontrol Akses) [cite: 544]
    function setAccessPermission(address _doctorAddress, bool _hasPermission) public {
        // Kontrol akses: Hanya pasien (msg.sender) yang bisa mengubah izin datanya
        accessPermissions[msg.sender][_doctorAddress] = _hasPermission;
        // Transaksi ini mencatat jejak persetujuan pasien [cite: 432]
    }

    // Fungsi untuk Memeriksa Izin Akses (Dipanggil oleh Backend Flask)
    function checkPermission(address _patientAddress, address _doctorAddress, string memory _action) public view returns (bool) {
        // Jika aksinya adalah READ/CRUD data medis:
        if (keccak256(abi.encodePacked(_action)) == keccak256(abi.encodePacked("READ_MEDICAL_RECORD"))) {
            return accessPermissions[_patientAddress][_doctorAddress];
        }
        // Logika lain untuk aksi lain...
        return false;
    }
}