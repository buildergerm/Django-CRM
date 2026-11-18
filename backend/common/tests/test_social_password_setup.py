"""One-time password setup for newly registered social-login accounts."""

import pytest
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import status


@pytest.mark.django_db
class TestSocialPasswordSetup:
    url = "/api/auth/social/set-password/"

    def test_valid_token_sets_password_and_invalidates_token(
        self, unauthenticated_client, admin_user
    ):
        token = PasswordResetTokenGenerator().make_token(admin_user)
        response = unauthenticated_client.post(
            self.url,
            {
                "uid": str(admin_user.pk),
                "token": token,
                "password": "Violet-Cedar-Orbit-2026!qX",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        admin_user.refresh_from_db()
        assert admin_user.check_password("Violet-Cedar-Orbit-2026!qX")

        replay = unauthenticated_client.post(
            self.url,
            {
                "uid": str(admin_user.pk),
                "token": token,
                "password": "Amber-Comet-Forest-2027!mN",
            },
            format="json",
        )
        assert replay.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_token_is_rejected(self, unauthenticated_client, admin_user):
        response = unauthenticated_client.post(
            self.url,
            {
                "uid": str(admin_user.pk),
                "token": "not-a-valid-token",
                "password": "Violet-Cedar-Orbit-2026!qX",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_short_password_is_rejected(self, unauthenticated_client, admin_user):
        token = PasswordResetTokenGenerator().make_token(admin_user)
        response = unauthenticated_client.post(
            self.url,
            {
                "uid": str(admin_user.pk),
                "token": token,
                "password": "short",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
