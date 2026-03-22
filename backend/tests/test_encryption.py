from backend.services.encryption import EncryptionService


def test_encrypt_decrypt_roundtrip():
    service = EncryptionService()
    plaintext = "my-secret-password"
    encrypted = service.encrypt(plaintext)
    assert encrypted != plaintext
    assert service.decrypt(encrypted) == plaintext


def test_encrypt_returns_different_ciphertext():
    service = EncryptionService()
    a = service.encrypt("password")
    b = service.encrypt("password")
    assert a != b


def test_encrypt_none_returns_none():
    service = EncryptionService()
    assert service.encrypt(None) is None
    assert service.decrypt(None) is None


def test_mask():
    assert EncryptionService.mask("anything") == "***"
    assert EncryptionService.mask(None) is None
