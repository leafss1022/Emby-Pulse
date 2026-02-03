from name_mappings import NameMappingService


def main() -> None:
    service = NameMappingService()
    service._mappings = {
        "clients": {
            "Emby Web": "Web",
            "Emby Web (Chrome)": "Web",
        },
        "devices": {
            "Mozilla Firefox Windows": "Firefox",
            "Mozilla Firefox Linux": "Firefox",
        },
    }
    service._loaded = True

    assert service.map_client_name("Emby Web") == "Web"
    assert service.expand_client_filters(["Web"]) == ["Emby Web", "Emby Web (Chrome)"]
    assert service.expand_client_filters(["Emby Web"]) == ["Emby Web", "Emby Web (Chrome)"]
    assert service.expand_client_filters(["Other"]) == ["Other"]

    assert service.map_device_name("Mozilla Firefox Linux") == "Firefox"
    assert service.expand_device_filters(["Firefox"]) == ["Mozilla Firefox Linux", "Mozilla Firefox Windows"]
    assert service.expand_device_filters(["Mozilla Firefox Windows"]) == [
        "Mozilla Firefox Linux",
        "Mozilla Firefox Windows",
    ]

    print("OK")


if __name__ == "__main__":
    main()

