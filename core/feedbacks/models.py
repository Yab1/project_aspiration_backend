import os

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import BaseModel
from core.users.models import Member


class Feedback(BaseModel):
    author = models.ForeignKey(Member, on_delete=models.CASCADE)
    comment = models.TextField(
        "Your Comment",
        help_text=_("Type your feedback here..."),
    )
    e_signature = models.ImageField(
        "E Signature",
        upload_to="",
        help_text=_("Upload the author signature."),
    )
    digital_signature = models.BinaryField(
        "Digital Signature",
        editable=False,
        null=True,
        blank=True,
        help_text=_("The digital signature of the feedback."),
    )
    public_key = models.TextField(
        "Public Key",
        editable=False,
        null=True,
        blank=True,
        help_text=_("The public key for verifying the digital signature."),
    )

    def __str__(self) -> str:
        return self.author.full_name

    def save(self, *args, **kwargs):
        # Generate RSA key pair
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()

        # Serialize and save the public key
        self.public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        # Save the private key to a secure location (for illustration)
        private_key_path = f"private_keys/{self.author.id}_private_key.pem"
        os.makedirs(os.path.dirname(private_key_path), exist_ok=True)
        with open(private_key_path, "wb") as key_file:
            key_file.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                ),
            )

        # Combine the comment and signature path
        data_to_sign = f"{self.comment}|{self.e_signature.url}"

        # Debug: Print the data to verify
        print(f"Data to sign: {data_to_sign}")

        # Hash the combined data
        message = data_to_sign.encode("utf-8")
        digest = hashes.Hash(hashes.SHA256())
        digest.update(message)
        hashed_comment = digest.finalize()

        # Debug: Print the hashed data for verification
        print(f"Hashed data: {hashed_comment}")
        # Sign the hashed comment
        self.digital_signature = private_key.sign(
            hashed_comment,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )

        # Save the model instance
        super().save(*args, **kwargs)

    def verify_signature(self):
        # Load the public key
        public_key = serialization.load_pem_public_key(self.public_key.encode("utf-8"))

        # Combine the comment and signature path
        data_to_verify = f"{self.comment}|{self.e_signature.url}"

        # Debug: Print the data to verify
        print(f"Data to verify: {data_to_verify}")
        # Hash the combined data
        message = data_to_verify.encode("utf-8")
        digest = hashes.Hash(hashes.SHA256())
        digest.update(message)
        hashed_comment = digest.finalize()

        # Debug: Print the hashed data for verification
        print(f"Hashed data for verification: {hashed_comment}")

        try:
            # Verify the digital signature
            public_key.verify(
                self.digital_signature,
                hashed_comment,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                Prehashed(hashes.SHA256()),
            )
            print("Verification successful!")
            return True
        except Exception as e:
            print(f"Verification failed: {e}")
            return False
