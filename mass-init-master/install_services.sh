DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

install_service () {
    service=$1
    sudo systemctl stop ${service}.service
    sudo systemctl disable ${service}.service
    sudo rm -f /etc/systemd/system/${service}.service
    sudo rm -f /usr/local/bin/${service}.sh
    echo "Removed old ${service} service"
    sudo cp $DIR/services/${service}.service /etc/systemd/system/${service}.service
    sudo cp $DIR/services/${service}.sh /usr/local/bin/${service}.sh
    sudo chmod +x /usr/local/bin/${service}.sh
    sudo systemctl enable ${service}.service
    sudo systemctl start ${service}.service

    echo "Installed ${service} service"
}

install_service "ros-px"
install_service "ros-epn"
install_service "ros-sensors"
install_service "ros-panel"
