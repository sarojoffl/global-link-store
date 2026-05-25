import base64
import hashlib
import hmac


def generate_esewa_signature(secret_key, data_dict, signed_fields):
    message = ",".join(f"{field}={data_dict[field]}" for field in signed_fields)
    signature = hmac.new(
        secret_key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(signature).decode("utf-8")


def verify_esewa_signature(secret_key, data_dict, signed_fields, received_signature):
    expected = generate_esewa_signature(secret_key, data_dict, signed_fields)
    return hmac.compare_digest(expected, received_signature)