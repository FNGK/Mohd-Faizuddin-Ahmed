import pyotp


def generate_secret() -> str:
    return pyotp.random_base32()


def provisioning_uri(secret: str, email: str, issuer: str = "SEO With Faiz CMS") -> str:
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)


def verify_code(secret: str, code: str) -> bool:
    if not secret or not code:
        return False
    totp = pyotp.TOTP(secret)
    return totp.verify(code.strip().replace(" ", ""), valid_window=1)
