import sys
import types
import logging

# Monkey-patch for cryptography compatibility with older versions of cryptncompress
# Newer cryptography (35+) moved RSA classes from hazmat.backends.openssl.rsa 
# to hazmat.primitives.asymmetric.rsa.
try:
    from cryptography.hazmat.primitives.asymmetric import rsa
    import cryptography.hazmat.backends as backends
    
    # Ensure cryptography.hazmat.backends.openssl exists
    try:
        import cryptography.hazmat.backends.openssl as openssl
    except ImportError:
        openssl = types.ModuleType("openssl")
        sys.modules["cryptography.hazmat.backends.openssl"] = openssl
        # Also attach it to the parent module if possible
        if hasattr(backends, "__path__"):
            backends.openssl = openssl
    
    # Ensure cryptography.hazmat.backends.openssl.rsa exists
    try:
        import cryptography.hazmat.backends.openssl.rsa
    except ImportError:
        sys.modules["cryptography.hazmat.backends.openssl.rsa"] = rsa
        # Also attach it to the parent module
        openssl.rsa = rsa
        
except ImportError:
    # If cryptography is not installed, we let it fail naturally when imported later
    pass
except Exception as e:
    # Use a basic print if logging is not yet configured
    print(f"Warning: Failed to apply cryptography monkey-patch: {e}", file=sys.stderr)
