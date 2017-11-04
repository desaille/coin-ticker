#! /bin/sh
# /etc/init.d/cointicker

case "$1" in
  start)
    echo "Starting CoinTicker"
    # run application you want to start
    python /opt/coin-ticker/TickerDisplay.py >> /var/log/cointicker.log 2>&1 &
    ;;
  stop)
    echo "Stopping Cointicker"
    # kill application you want to stop
    killall python
    ;;
  *)
    echo "Usage: /etc/init.d/example{start|stop}"
    exit 1
    ;;
esac

exit 0