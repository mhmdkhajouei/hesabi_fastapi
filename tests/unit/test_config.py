import pytest

from app.config import Settings


class TestSettingsDatabaseUrl:
    def test_database_url_standard_values(self):
        conf = Settings(
            db_user="hesabi_admin",
            db_password="SafePassword2026",
            db_host="localhost",
            db_port=5432,
            db_name="hesabi_db",
        )
        expected = "postgresql+asyncpg://hesabi_admin:SafePassword2026@localhost:5432/hesabi_db"
        assert conf.database_url == expected

    @pytest.mark.parametrize(
        "user, password, host, port, db_name, expected_url",
        [
            (
                "postgres",
                "root_1234",
                "127.0.0.1",
                5433,
                "finance_test",
                "postgresql+asyncpg://postgres:root_1234@127.0.0.1:5433/finance_test",
            ),
            (
                "cloud_user",
                "P@ss#w0rd!_complex",
                "db.internal.company.lan",
                6432,
                "hesabi_production",
                "postgresql+asyncpg://cloud_user:P@ss#w0rd!_complex@db.internal.company.lan:6432/hesabi_production",
            ),
            (
                "service_account_1",
                "simplepass",
                "postgres_container",
                5432,
                "hesabi_stage",
                "postgresql+asyncpg://service_account_1:simplepass@postgres_container:5432/hesabi_stage",
            ),
        ],
    )
    def test_database_url_parametrized_configurations(
        self, user, password, host, port, db_name, expected_url
    ):
        conf = Settings(
            db_user=user,
            db_password=password,
            db_host=host,
            db_port=port,
            db_name=db_name,
        )
        assert conf.database_url == expected_url

    def test_database_url_cached_property_integrity(self):
        conf = Settings(
            db_user="initial_user",
            db_password="initial_pass",
            db_host="localhost",
            db_port=5432,
            db_name="initial_db",
        )

        first_eval = conf.database_url
        assert "initial_user" in first_eval

        conf.db_user = "manipulated_user"
        assert conf.database_url == first_eval
        assert "manipulated_user" not in conf.database_url

        del conf.database_url
        assert "manipulated_user" in conf.database_url
