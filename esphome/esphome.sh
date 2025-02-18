#docker run --rm --net=host -v "${PWD}":/config -it ghcr.io/esphome/esphome
docker run --rm -p 6052:6052 -p 8266:8266 -p 6053:6053 -e ESPHOME_DASHBOARD_USE_PING=true -v "${PWD}":/config -it ghcr.io/esphome/esphome

