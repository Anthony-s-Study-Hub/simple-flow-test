from simple_flow_test_app.health import health_payload


def test_health_payload_reports_ok() -> None:
    assert health_payload() == {"status": "ok"}
