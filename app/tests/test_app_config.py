from app_config import AppConfig, get_app_config


class TestAppConfig:
    def test_get_app_config(self):
        app_config = get_app_config()
        assert app_config == AppConfig(
            canvas_domain="https://canvas.narxoz.kz",
            encryption_key="Z8qWK_Ce5OOBuISsa2j35UMf6z_a7jkwI3VTAXQj31g=",
            secure_key="a8qWK_Ce5OOBuISsa2j35UMf6z_a7jkwI3VTAXQj31g=",
        )
