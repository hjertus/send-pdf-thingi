sudo docker build -t listenandprint .
sudo docker run --privileged -d --restart always --device=/dev/bus/usb/<BUS_NUMBER>/<DEVICE_NUMBER> -e SECRET_KEY=<secret_key> listenandprint

